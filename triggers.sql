DELIMITER //

CREATE TRIGGER before_enrollment_update
BEFORE UPDATE ON Enrollments
FOR EACH ROW
BEGIN
    -- Calculate Total Marks
    SET NEW.total_marks = NEW.quiz_marks + NEW.midterm_marks + NEW.final_marks;

    -- Calculate Grade
    IF NEW.total_marks >= 90 THEN
        SET NEW.grade = 'A';
    ELSEIF NEW.total_marks >= 80 THEN
        SET NEW.grade = 'B';
    ELSEIF NEW.total_marks >= 70 THEN
        SET NEW.grade = 'C';
    ELSEIF NEW.total_marks >= 60 THEN
        SET NEW.grade = 'D';
    ELSE
        SET NEW.grade = 'F';
    END IF;
END;
//

DELIMITER ;
