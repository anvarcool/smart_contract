import { keccak256, toUtf8Bytes } from "ethers";
import { loadFixture, ethers, expect } from "./setup";

describe("education_system", function() {
    
    async function deploy() {
        const [user1, user2, user3, user4] = await ethers.getSigners();
        const Factory = await ethers.getContractFactory("Education_system");
        const education_system = await Factory.deploy();
        await education_system.waitForDeployment();
        return {user1, user2, user3, user4, education_system}
    }

    it("should be deployed", async function(){
        const {education_system} = await loadFixture(deploy);
        await expect(education_system.target).to.be.properAddress;
    });

    it("should add new teacher", async function(){
        const {user1, user2, user3, education_system} = await loadFixture(deploy);
        await education_system.connect(user1).add_person(user2.address, true);
        const val = await education_system._isTeacher(user2.address);
        await expect(val).to.eq(true);
    });

    it("should add new teacher", async function(){
        const {user1, user2, user3, education_system} = await loadFixture(deploy);
        await education_system.connect(user1).add_person(user3.address, false);
        const val = await education_system._isStudent(user3.address);
        await expect(val).to.eq(true);
    });

    it("should create a new course", async function () {
        const { user1, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        await education_system.connect(user1).create_course(courseName);
        const newcourse = await education_system.all_courses(courseName);
        await expect(newcourse).to.eq(courseName);
    });

    it("should assign teacher to course", async function () {
        const { user1, user2, education_system } = await loadFixture(deploy);
        const course_name = "Распределенные реестры";
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).create_course(course_name);
        await education_system.connect(user1).define_course_teachers(user2.address, course_name);

        const teachers = await education_system.get_course_teachers(course_name);
        await expect(teachers).to.include(user2.address);
    });

    it("should allow student to attend course", async function () {
        const { user1, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user3).attend_course(courseName);

        const queue = await education_system.queue_getter(courseName);
        await expect(queue).to.include(user3.address);
    });

    it("should approve student for course", async function () {
        const { user1, user2, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user3).attend_course(courseName);
        await education_system.connect(user2).approve_student(user3.address, courseName);

        const stud = await education_system.get_course_students(courseName);
        await expect(stud).to.include(user3.address);
    });

    it("should add lesson to the course", async function () {
        const { user1, user2, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const lessonTimestamp = 17000n;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user2).add_lesson(courseName, lessonTimestamp);

        const sched = await education_system.get_course_schedule(courseName);
        await expect(sched).to.include(lessonTimestamp);
    });

    it("should remove a lesson from the course schedule", async function () {
        const { user1, user2, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const lessonTimestamp = 1234567n;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user2).add_lesson(courseName, lessonTimestamp);
        await education_system.connect(user2).add_lesson(courseName, 222222n);
        await education_system.connect(user2).remove_lesson(courseName, lessonTimestamp);
        const sched = await education_system.get_course_schedule(courseName);
        await expect(sched).not.to.include(lessonTimestamp);
    });

    it("should edit a lesson in the course schedule", async function () {
        const { user1, user2, education_system } = await loadFixture(deploy);
        const courseName = "Blockchain Basics";
        const oldTimestamp = 1234567n;
        const newTimestamp = 7777777n;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user2).add_lesson(courseName, oldTimestamp);

        await education_system.connect(user2).edit_lesson(courseName, oldTimestamp, newTimestamp);
        const sched = await education_system.get_course_schedule(courseName);
        await expect(sched).to.include(newTimestamp);
        await expect(sched).not.to.include(oldTimestamp);
    });

    it("should mark student presence", async function () {
        const { user1, user2, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user3).attend_course(courseName);
        await education_system.connect(user2).approve_student(user3.address, courseName);

        await education_system.connect(user2).student_presence(user3.address, courseName);
        const presenceCount = await education_system.presence_getter(user3.address, courseName);
        await expect(presenceCount).to.eq(1);
    });

    it("should mark student grade", async function () {
        const { user1, user2, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const date = 1234567n;
        const mark = 4;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user3).attend_course(courseName);
        await education_system.connect(user2).approve_student(user3.address, courseName);

        await education_system.connect(user2).mark_student(user3.address, courseName, date, mark);

        const marks = await education_system.check_person_marks(user3.address, date, date);
        await expect(marks[0].mark).to.eq(mark);
    });


    it("should return person schedule filter by date", async function () {
        const { user1, user2, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const lessonTimestamp = 1234567n;
        const startDt = 1200000n;
        const endDt = 1300000n;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user3).attend_course(courseName);
        await education_system.connect(user2).approve_student(user3.address, courseName);
        await education_system.connect(user2).add_lesson(courseName, lessonTimestamp);

        const schedule = await education_system.check_persons_schedule(user3.address, startDt, endDt);
        expect(schedule).to.have.length(1);
        expect(schedule[0].course_name).to.eq(courseName);
        expect(schedule[0].schedule).to.include(lessonTimestamp);
    });

    it("should return course schedule filter by date", async function () {
        const { user1, user2, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const lessonTimestamp = 1234567n;
        const startDt = 1200000n;
        const endDt = 1300000n;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user2).add_lesson(courseName, lessonTimestamp);

        const filteredSchedule = await education_system.check_course_schedule(courseName, startDt, endDt);
        expect(filteredSchedule).to.include(lessonTimestamp);
    });

    it("should return student marks filter by date", async function () {
        const { user1, user2, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const date = 1234567n;
        const mark = 4;
        const startDt = 1200000n;
        const endDt = 1300000n;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user3).attend_course(courseName);
        await education_system.connect(user2).approve_student(user3.address, courseName);
        await education_system.connect(user2).mark_student(user3.address, courseName, date, mark);

        const marks = await education_system.check_person_marks(user3.address, startDt, endDt);
        expect(marks).to.have.length(1);
        expect(marks[0].mark).to.eq(mark);
    });

    it("should return course marks filter by date", async function () {
        const { user1, user2, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const markDate = 1234567n;
        const mark = 5;
        const startDt = 1200000n;
        const endDt = 1300000n;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user3).attend_course(courseName);
        await education_system.connect(user2).approve_student(user3.address, courseName);
        await education_system.connect(user2).mark_student(user3.address, courseName, markDate, mark);

        const courseMarks = await education_system.check_course_marks(courseName, startDt, endDt);
        expect(courseMarks).to.have.length(1);
        expect(courseMarks[0].mark).to.eq(mark);
    });

    it("should calculate student statistics", async function () {
        const { user1, user2, user3, education_system } = await loadFixture(deploy);
        const courseName = "Распределенные реестры";
        const markDate1 = 123456n;
        const mark1 = 5;
        const markDate2 = 333456n;
        const mark2 = 3;
        await education_system.connect(user1).add_person(user2.address, true);
        await education_system.connect(user1).add_person(user3.address, false);
        await education_system.connect(user1).create_course(courseName);
        await education_system.connect(user1).define_course_teachers(user2.address, courseName);
        await education_system.connect(user3).attend_course(courseName);
        await education_system.connect(user2).approve_student(user3.address, courseName);
        await education_system.connect(user2).mark_student(user3.address, courseName, markDate1, mark1);
        await education_system.connect(user2).mark_student(user3.address, courseName, markDate2, mark2);
        
        await education_system.connect(user2).student_presence(user3.address, courseName);
        await education_system.connect(user2).student_presence(user3.address, courseName);
        await education_system.connect(user2).student_presence(user3.address, courseName);
        await education_system.connect(user2).student_presence(user3.address, courseName);


        const stats = await education_system.student_statistics(user3.address);
        const res = await education_system.results_getter(courseName);
        await expect(res).to.eq(400);
    });
});