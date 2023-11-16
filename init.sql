CREATE TABLE pg.SoCs (
    id INT PRIMARY KEY,
    Model VARCHAR(255),
    Date_out DATE,
    Tdp NUMERIC(10,2),
    Core_count INT
);

INSERT INTO pg.SoCs (id, Model, Date_out, TDP, Core_count)
VALUES
    (1, 'Snapdragon 730G', '2020-01-01', 50.5, 8),
    (2, 'Snapdragon 730', '2019-05-15', 45.2, 8),
    (3, 'Apple A17 Pro', '2023-09-22', 60.0, 12);

CREATE TABLE pg.Phones (
    id INT PRIMARY KEY,
    Model VARCHAR(255),
    Date_out DATE,
    Used_SoC INT NOT null,
    FOREIGN KEY (Used_SoC) REFERENCES pg.SoCs(id),
    Camera_count INT,
    Mass NUMERIC(10,2)
);

INSERT INTO pg.Phones (id, Model, Date_out, Used_SoC, Camera_count, Mass)
VALUES
    (1, 'Xiaomi mi note 10', '2020-03-15', 1, 4, 150.5),
    (2, 'Apple Iphone 15', '2021-11-20', 2, 3, 130.2),
    (3, 'Xiaomi mi9T', '2023-05-10', 3, 3, 160.0);