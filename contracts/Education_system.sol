pragma solidity = 0.8.26;

contract Utils{
    constructor() {
    }
    function toString(uint256 value) public pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
 
        uint256 temp = value;
        uint256 digits;
 
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
 
        bytes memory buffer = new bytes(digits);
 
        while (value != 0) {
            digits--;
            buffer[digits] = bytes1(uint8(48 + (value % 10)));
            value /= 10;
        }
 
        return string(buffer);
    }
}

contract Roles is Utils{
    

    address public admin;
    mapping (address => bool) public _isTeacher;
    mapping (address => bool) public _isStudent;
    mapping (string => course) public all_courses;
    
    struct course{
        string course_name;
        address[] teachers;
        address[] students;
        uint[] schedule;
    }


    function get_course_teachers(string memory currcourse) public view returns(address[] memory){
        return all_courses[currcourse].teachers;
    }

     function get_course_students(string memory currcourse) public view returns(address[] memory){
        return all_courses[currcourse].students;
    }

    function get_course_schedule(string memory currcourse) public view returns(uint[] memory){
        return all_courses[currcourse].schedule;
    }

    constructor() {
        admin = msg.sender; //admin - тот кто отправил транзакцию по созданию контракта
    }


    event new_person(address person, string role);


    modifier onlyAdmin(){
        require(msg.sender == admin);
        _;
    }

    modifier isTeacher(address person_adr){
        require(_isTeacher[person_adr]);
        _;
    }

    modifier isStudent(address person_adr){
        require(_isStudent[person_adr]);
        _;
    }

    modifier isCourseTeacher(address teacher, string memory course_name){
        bool flag = false;
        uint l = all_courses[course_name].teachers.length;
        for (uint i = 0; i < l; i++){
            if (all_courses[course_name].teachers[i] == teacher){
                flag = true;
                break;
            }
        }
        require(flag);
        _;
    }

    modifier isCourseStudent(address student, string memory course_name){
    bool flag = false;
    uint l = all_courses[course_name].students.length;
    for (uint i = 0; i < l; i++){
        if (all_courses[course_name].students[i] == student){
            flag = true;
            break;
        }
    }
    require(flag);
    _;
}

    function add_person(address person, bool isteacher) onlyAdmin() public{
        string memory role;
        _isTeacher[person] = isteacher;  
        if (isteacher){
            role = "Teacher";
            _isTeacher[person] = true;  
        }
        else{
            _isStudent[person] = true;  
            role = "Student";   
        }
        emit new_person(person, role);
    }
}


contract Education_system is Roles{

    mapping (string => address[]) public students_waiting_approval;
    mapping (address => string[]) public person_courses;
    mapping (address => mapping(string => uint)) public presence;
    
    struct Schedule{
        string course_name;
        uint[] schedule;
    }

    struct Mark{
        string course_name;
        address student;
        uint date;
        uint mark;
    }

    mapping (address => Mark[]) person_marks;
    mapping (string => Mark[]) course_marks;
    mapping (string  => uint[2]) public sum_num_marks;

    event new_course(string course_name);

    function presence_getter(address student, string memory course_name) public view returns (uint){
        return presence[student][course_name];
    }
    function create_course(string memory course_name) onlyAdmin() public{
        course memory added_course;
        added_course.course_name = course_name;
        all_courses[course_name] = added_course;
        emit new_course(course_name);
    }

    function queue_getter(string memory arg) public view returns (address[] memory){
        return students_waiting_approval[arg];
    }

    function define_course_teachers(address teacher, string memory course_name) public onlyAdmin() isTeacher(teacher) {
        all_courses[course_name].teachers.push(teacher);
        person_courses[teacher].push(course_name);
    }

    function attend_course(string memory course_name) isStudent(msg.sender) public{
        students_waiting_approval[course_name].push(msg.sender);
    }

    function view_course_queue(string memory course_name) isCourseTeacher(msg.sender, course_name) public view returns (address[] memory){ 
        return students_waiting_approval[course_name];
    }

    function approve_student(address student, string memory course_name) public isCourseTeacher(msg.sender, course_name) isStudent(student){
        address[] memory queue_for_curr_course = students_waiting_approval[course_name];
        uint l = queue_for_curr_course.length;
        for (uint i = 0; i < l; i++){
            if (queue_for_curr_course[i] == student){
                delete students_waiting_approval[course_name][i];
                all_courses[course_name].students.push(student);
                person_courses[student].push(course_name);
                break;
            }
        }
    }

    function add_lesson(string memory course_name, uint datetime) public isCourseTeacher(msg.sender, course_name){
        // datetime - дата и время в формате timestamp
        all_courses[course_name].schedule.push(datetime);
    }

    function remove_lesson(string memory course_name, uint datetime) public isCourseTeacher(msg.sender, course_name){
        // datetime - дата и время в формате timestamp
        uint[] memory schedule = all_courses[course_name].schedule;
        for (uint i = 0; i < schedule.length; i++){
            if (schedule[i] == datetime){
                delete all_courses[course_name].schedule[i];
                break;
            }
        }
    }

    function edit_lesson(string memory course_name, uint datetime_old, uint datetime_new) public isCourseTeacher(msg.sender, course_name){
        // datetime - дата и время в формате timestamp
        uint[] memory schedule = all_courses[course_name].schedule;
        for (uint i = 0; i < schedule.length; i++){
            if (schedule[i] == datetime_old){
                all_courses[course_name].schedule[i] = datetime_new;
                break;
            }
        }
    }
    function check_persons_schedule(address person, uint start_dt, uint end_dt) public view returns(Schedule[] memory persons_schedule){
        // start_dt, end_dt - дата и время в формате timestamp
        string[] memory courses = person_courses[person];
        persons_schedule = new Schedule[](courses.length);
        uint k;
        for(uint i = 0; i < courses.length; i++){
            k = 0;
            uint[] memory current_schedule = all_courses[courses[i]].schedule;
            for (uint j = 0; j < current_schedule.length; j++){
                if ((current_schedule[j] >= start_dt) && (current_schedule[j] <= end_dt))
                    k++;
            }
            uint[] memory filtered_schedule = new uint[](k);
            k = 0;
            for (uint j = 0; j < current_schedule.length; j++){
                if ((current_schedule[j] >= start_dt) && (current_schedule[j] <= end_dt)){
                    filtered_schedule[k] = current_schedule[j];
                    k++;
                }
            }
            persons_schedule[i] = (Schedule(courses[i], filtered_schedule));    
        return persons_schedule;
        }
    }

    function check_course_schedule(string memory course_name, uint start_dt, uint end_dt) public view returns(uint[] memory filtered_schedule){  
        uint[] memory current_schedule = all_courses[course_name].schedule;
        uint k = 0;
        for (uint j = 0; j < current_schedule.length; j++){
            if ((current_schedule[j] >= start_dt) && (current_schedule[j] <= end_dt))
                k++;
        }
        filtered_schedule = new uint[](k);
        k = 0;
        for (uint j = 0; j < current_schedule.length; j++){
            if ((current_schedule[j] >= start_dt) && (current_schedule[j] <= end_dt)){
                filtered_schedule[k] = current_schedule[j];
                k++;
            }
        }
        return filtered_schedule;
    }

    function student_presence(address student, string memory course_name) public isCourseTeacher(msg.sender, course_name) 
                                                                            isCourseStudent(student, course_name){
        presence[student][course_name]++;
    }
    
    function mark_student (address student, string memory course_name, uint date, uint mark) public isCourseTeacher(msg.sender, course_name) 
                                                                            isCourseStudent(student, course_name){
        course_marks[course_name].push(Mark(course_name, student, date, mark));
        person_marks[student].push(Mark(course_name, student, date, mark));
        person_marks[msg.sender].push(Mark(course_name, student, date, mark));
    }

    function check_person_marks(address person, uint start_dt, uint end_dt) public view returns(Mark[] memory filtered_marks){
        // start_dt, end_dt - дата и время в формате timestamp
        Mark[] memory marks = person_marks[person];
        uint k;
        k = 0;
        for (uint j = 0; j < marks.length; j++){
            if ((marks[j].date >= start_dt) && (marks[j].date <= end_dt))
                k++;
        }
        filtered_marks = new Mark[](k);
        k = 0;
        for (uint j = 0; j < marks.length; j++){
            if ((marks[j].date >= start_dt) && (marks[j].date <= end_dt)){
                filtered_marks[k] = marks[j];
                k++;
            }
        }
        return filtered_marks;
    }

    function check_course_marks(string memory course_name, uint start_dt, uint end_dt) public view returns(Mark[] memory filtered_marks){
        // start_dt, end_dt - дата и время в формате timestamp
        Mark[] memory marks = course_marks[course_name];
        uint k;
        k = 0;
        for (uint j = 0; j < marks.length; j++){
            if ((marks[j].date >= start_dt) && (marks[j].date <= end_dt))
                k++;
        }
        filtered_marks = new Mark[](k);
        k = 0;
        for (uint j = 0; j < marks.length; j++){
            if ((marks[j].date >= start_dt) && (marks[j].date <= end_dt)){
                filtered_marks[k] = marks[j];
                k++;
            }
        }
        return filtered_marks;
    }

    function student_statistics(address student) public returns(string[] memory results){
        string[] memory courses = person_courses[student];
        Mark[] memory marks = person_marks[student];
        for (uint i = 0; i < courses.length; i++){
            sum_num_marks[courses[i]][0] = 0;
            sum_num_marks[courses[i]][1] = 0;
        }
        for (uint i = 0; i < marks.length; i++){
            sum_num_marks[marks[i].course_name][0] += marks[i].mark;
            sum_num_marks[marks[i].course_name][1]++;
        }
        results = new string[](courses.length);
        for (uint j = 0; j < courses.length; j++){
            uint avg_mark = (sum_num_marks[courses[j]][0] * 100) / sum_num_marks[courses[j]][1];            
            string memory avg = string.concat(toString(avg_mark / 100), ".", toString(avg_mark % 100)) ;
            results[j] = string.concat(courses[j], " ", avg, " ",toString(presence[student][courses[j]]));
        }
        return results;
    }

    function results_getter(string memory courseName) public view returns(uint avg_mark){
        avg_mark = (sum_num_marks[courseName][0] * 100) / sum_num_marks[courseName][1];
        return (sum_num_marks[courseName][0] * 100) / sum_num_marks[courseName][1];
    }
}