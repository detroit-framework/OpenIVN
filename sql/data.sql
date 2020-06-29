INSERT INTO users(id, name, email)
VALUES ('001', 'George Washington', 'george.washington@usa.com');

INSERT INTO users(id, name, email)
VALUES ('002', 'John Adams', 'john.adams@usa.com');

INSERT INTO users(id, name, email)
VALUES ('003', 'Thomas Jefferson', 'thomas.jefferson@usa.com');

INSERT INTO users(id, name, email)
VALUES ('004', 'James Madison', 'james.madison@usa.com');

INSERT INTO apps(name, author_id, description, streaming)
VALUES ('America101', '001', 'Knowledge is in every country the surest basis of public happiness.', 0);

INSERT INTO apps(name, author_id, description, streaming, stream_endpoint)
VALUES ('Prez2', '002', 'I read my eyes out and can’t read half enough neither. The more one reads the more one sees we have to read.', 1, 'https://somewebsite.usa.com');

INSERT INTO apps(name, author_id, description, streaming)
VALUES ('Declaration', '003', 'On matters of style, swim with the current, on matters of principle, stand like a rock.', 0);

INSERT INTO apps(name, author_id, description, streaming, stream_endpoint)
VALUES ('Bill-o-Rights', '004', 'Philosophy is common sense with big words.', 1, 'https://anotherwebsite.usa.com');

INSERT INTO apps(name, author_id, description, streaming)
VALUES ('Test', '001', 'Manually Translating apps locally', 0);

INSERT INTO permissions(app_id, Acceleration, Battery, Doors, Engine_Information, Engine_Utilization, Fuel_Information, Gyroscope, HVAC, Hood, Lights, Mirrors, Parking_Brake, Pedal_Positions, Position_Information, Seat_Belts, Speed, Torque, Trunk, Vehicle_Turning, Windows, Windshield_Wipers)
VALUES(1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0);

INSERT INTO permissions(app_id, Acceleration, Battery, Doors, Engine_Information, Engine_Utilization, Fuel_Information, Gyroscope, HVAC, Hood, Lights, Mirrors, Parking_Brake, Pedal_Positions, Position_Information, Seat_Belts, Speed, Torque, Trunk, Vehicle_Turning, Windows, Windshield_Wipers)
VALUES(2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

INSERT INTO permissions(app_id, Acceleration, Battery, Doors, Engine_Information, Engine_Utilization, Fuel_Information, Gyroscope, HVAC, Hood, Lights, Mirrors, Parking_Brake, Pedal_Positions, Position_Information, Seat_Belts, Speed, Torque, Trunk, Vehicle_Turning, Windows, Windshield_Wipers)
VALUES(3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0);

INSERT INTO permissions(app_id, Acceleration, Battery, Doors, Engine_Information, Engine_Utilization, Fuel_Information, Gyroscope, HVAC, Hood, Lights, Mirrors, Parking_Brake, Pedal_Positions, Position_Information, Seat_Belts, Speed, Torque, Trunk, Vehicle_Turning, Windows, Windshield_Wipers)
VALUES(4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);

INSERT INTO permissions(app_id, Acceleration, Battery, Doors, Engine_Information, Engine_Utilization, Fuel_Information, Gyroscope, HVAC, Hood, Lights, Mirrors, Parking_Brake, Pedal_Positions, Position_Information, Seat_Belts, Speed, Torque, Trunk, Vehicle_Turning, Windows, Windshield_Wipers)
VALUES(5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0);

INSERT INTO vehicles(vehicle_id, make, model, year, dbc)
VALUES('Make_Model1_2000', 'Make', 'Model1', 2000, 1);

INSERT INTO vehicles(vehicle_id, make, model, year, dbc)
VALUES('Make_Model2_2001', 'Make', 'Model2', 2001, 1);
