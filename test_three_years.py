import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from db.models import Base, AcademicYear
    from genetic_algorithm import GeneticScheduler
    import pandas as pd
    
    print("=== اختبار إنشاء جداول لثلاث سنوات ===")
    
    # إنشاء قاعدة البيانات
    engine = create_engine('sqlite:///university_scheduler.db')
    Base.metadata.create_all(engine)
    
    # إنشاء جلسة
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # البحث عن السنوات الأكاديمية
        academic_years = session.query(AcademicYear).order_by(AcademicYear.id).limit(3).all()
        
        if len(academic_years) < 3:
            print(f"تحذير: يوجد فقط {len(academic_years)} سنة أكاديمية")
            print("يرجى إضافة المزيد من السنوات الأكاديمية")
            sys.exit(1)
        
        print(f"تم العثور على {len(academic_years)} سنة أكاديمية:")
        for year in academic_years:
            print(f"  - {year.name} (ID: {year.id})")
        
        # قائمة لتخزين الجداول المولدة
        generated_schedules = []
        
        # إنشاء جداول لكل سنة
        for i, academic_year in enumerate(academic_years, 1):
            print(f"\n{'='*50}")
            print(f"إنشاء جدول للسنة {i}: {academic_year.name}")
            print(f"{'='*50}")
            
            # إنشاء الخوارزمية
            scheduler = GeneticScheduler(
                session=session,
                academic_year_id=academic_year.id,
                population_size=15,
                generations=20,
                mutation_rate=0.1,
                elite_size=3
            )
            
            # تشغيل الخوارزمية
            best_individual, best_fitness = scheduler.run()
            
            if best_individual:
                print(f"✅ تم إنشاء جدول بنجاح!")
                print(f"   - درجة الملاءمة: {best_fitness:.4f}")
                print(f"   - عدد الفترات: {len(best_individual)}")
                
                # حفظ الجدول
                schedule_name = f"جدول السنة {i} - {academic_year.name}"
                saved_schedule = scheduler.save_schedule(best_individual, schedule_name)
                print(f"   - تم حفظ الجدول: {saved_schedule.id}")
                
                # إضافة الجدول إلى القائمة
                generated_schedules.append({
                    'year': academic_year,
                    'schedule': saved_schedule,
                    'individual': best_individual,
                    'fitness': best_fitness
                })
                
                # عرض الجدول
                print(f"\n   الجدول:")
                df = scheduler.get_schedule_as_dataframe(best_individual)
                print(df)
                
            else:
                print(f"❌ فشل في إنشاء جدول للسنة {academic_year.name}")
        
        # فحص التعارضات بين جميع الجداول
        print(f"\n{'='*50}")
        print("فحص التعارضات بين جميع الجداول")
        print(f"{'='*50}")
        
        # إنشاء خوارزمية للفحص
        final_scheduler = GeneticScheduler(
            session=session,
            academic_year_id=academic_years[0].id,
            population_size=5,
            generations=5
        )
        
        print("\n1. فحص جميع التعارضات في قاعدة البيانات:")
        all_conflicts = final_scheduler.check_app_conflicts()
        
        # فحص التعارضات بين المدرسين
        print(f"\n2. فحص تعارضات المدرسين بين الجداول:")
        
        # تجميع جميع الفترات
        all_slots = []
        for schedule_info in generated_schedules:
            for slot in schedule_info['individual']:
                all_slots.append({
                    'teacher_id': slot['teacher'].id,
                    'teacher_name': slot['teacher'].name,
                    'year': schedule_info['year'].name,
                    'day': slot['day'],
                    'start_time': slot['start_time'],
                    'end_time': slot['end_time'],
                    'course': slot['course'].name
                })
        
        # فحص التعارضات
        teacher_conflicts = {}
        for i, slot1 in enumerate(all_slots):
            for j, slot2 in enumerate(all_slots):
                if i >= j:
                    continue
                
                # فحص تعارض نفس المدرس في نفس الوقت
                if (slot1['teacher_id'] == slot2['teacher_id'] and
                    slot1['day'] == slot2['day'] and
                    slot1['start_time'] == slot2['start_time'] and
                    slot1['end_time'] == slot2['end_time']):
                    
                    conflict_key = (slot1['teacher_id'], slot1['day'], slot1['start_time'], slot1['end_time'])
                    if conflict_key not in teacher_conflicts:
                        teacher_conflicts[conflict_key] = []
                    
                    if slot1 not in teacher_conflicts[conflict_key]:
                        teacher_conflicts[conflict_key].append(slot1)
                    if slot2 not in teacher_conflicts[conflict_key]:
                        teacher_conflicts[conflict_key].append(slot2)
        
        # عرض التعارضات
        if teacher_conflicts:
            print(f"\n❌ تم العثور على {len(teacher_conflicts)} تعارض:")
            for conflict_key, slots in teacher_conflicts.items():
                teacher_id, day, start_time, end_time = conflict_key
                teacher_name = slots[0]['teacher_name']
                
                print(f"\nتعارض للمدرس {teacher_name}:")
                print(f"  اليوم: {day}")
                print(f"  الوقت: {start_time} - {end_time}")
                
                for slot in slots:
                    print(f"    - السنة: {slot['year']}")
                    print(f"      المادة: {slot['course']}")
        else:
            print("\n✅ لا توجد تعارضات بين المدرسين!")
        
        # ملخص نهائي
        print(f"\n{'='*50}")
        print("الملخص النهائي")
        print(f"{'='*50}")
        
        total_schedules = len(generated_schedules)
        perfect_schedules = sum(1 for s in generated_schedules if s['fitness'] == 1.0)
        conflict_free_schedules = sum(1 for s in generated_schedules if all(
            not final_scheduler.check_real_time_conflicts(
                slot['teacher'].id, slot['day'], slot['start_time'], slot['end_time']
            ) for slot in s['individual']
        ))
        
        print(f"إجمالي الجداول المولدة: {total_schedules}")
        print(f"الجداول المثالية (fitness = 1.0): {perfect_schedules}")
        print(f"الجداول بدون تعارضات فعلية: {conflict_free_schedules}")
        
        if conflict_free_schedules == total_schedules:
            print("🎉 جميع الجداول خالية من التعارضات!")
        else:
            print("⚠️ بعض الجداول تحتوي على تعارضات")
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        session.close()
        
except ImportError as e:
    print(f"خطأ في الاستيراد: {e}")
except Exception as e:
    print(f"خطأ عام: {e}")

print("\n=== انتهى الاختبار ===") 