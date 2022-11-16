-- Sample data for development

-- Sample users
INSERT INTO USERS VALUES ('peter_the_anteater', 'f1cd60174ee81b6bd1810143fd5ea4cdeabb246db2c18340fba84250e74004a4', 'panteater@uci.edu', '28d0b49bf09f8295617c4d37237d0a5a34b657e409fc06bbf77e425ee89d690d', 'peter', 'anteater', 'usr/profiles/peter_the_anteater.png');
INSERT INTO USERS VALUES ('octocat', 'b1963ead70a79a4232b46ffbf8eb7ade15d04522292a3028f2a63dd4513ac552', 'octocat@github.com', 'b1963ead70a79a4232b46ffbf8eb7ade15d04522292a3028f2a63dd4513ac552', 'octo', 'cat', 'usr/profiles/octocat.png');

-- Sample tasks
INSERT INTO TASKS VALUES (DEFAULT, 'Nature in the City', 'Take a walk in a local park or other natural area', TRUE);
INSERT INTO TASKS VALUES (DEFAULT, 'Today I learned...', 'Share something new that you learned about today. Remember, you learn something new everyday', TRUE);
INSERT INTO TASKS VALUES (DEFAULT, 'New cuisine', 'Eat at a local restaurant that you have never tried before. Did you like the food? How about the service? Would you eat there again?', TRUE);
INSERT INTO TASKS VALUES (DEFAULT, 'New jamz', 'Listen to a song or artist or album that you have never heard before. Did you like the music? Will you explore more like it?', TRUE);
INSERT INTO TASKS VALUES (DEFAULT, 'Healthy lifestyles', 'Share something you did that is a part of your healthy lifestyle. Whether you just finished a intense workout or are indulging is a plant-based smoothie, there is no judgment here.', TRUE);

-- Sample posts
INSERT INTO POSTS VALUES (DEFAULT, 'Check out the beautiful scenary here at Aldrich Park', 'usr/posts/peter_the_anteater/1.jpg', '2022-11-16 22:32:30.768626', 'peter_the_anteater', 1);
INSERT INTO POSTS VALUES (DEFAULT, 'Just ate at the Anteatery for the first time! The food was medicore, but the service was pretty fast. I will probably eat here again since it is close to my dorm.', 'usr/posts/peter_the_anteater/2.jpg', '2022-11-17 22:32:30.768626', 'peter_the_anteater', 3);
INSERT INTO POSTS VALUES (DEFAULT, 'Today I learned how to write a hello world program in Python!', 'usr/posts/octocat/3.png', '2022-11-18 22:32:30.768626', 'octocat', 2);
INSERT INTO POSTS VALUES (DEFAULT, 'Just completed a deep water swim in my favorite ocean!', 'usr/posts/octocat/4.jpg', '2022-11-19 22:32:30.768626', 'octocat', 5);

--Sample completions
INSERT INTO COMPLETES VALUES ('peter_the_anteater', 1);
INSERT INTO COMPLETES VALUES ('peter_the_anteater', 3);
INSERT INTO COMPLETES VALUES ('octocat', 2);
INSERT INTO COMPLETES VALUES ('octocat', 5);
