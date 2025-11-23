With lifestyles becoming busier than ever, staying at peace about your home 🏡 is crucial. Who needs to get in? What if the kids lose the keys? What if they arrive when we're out?

nok is the solution you need. It is an automated door opening system that lets authorized persons into your home. It watches for faces in front of the door, and if an authorized face is found, opens the door for them.

nok doesn't just open doors; it puts YOU in control. You always control who has access to your home. Anytime, you can add or remove access from people. And not just that, you can manually control the door and get notified if an unauthorized face is waiting at the door.

# What is nok?

nok is a system that opens doors (literally). Connected to cameras, it identifies faces at the door of your house and lets them in depending on whether you have given them access.

Complemented with a central server that processes requests and a mobile application providing access controls in your pocket, even when you are away.

# How it works?

nok contains four main elements:

- the *embedded module* connected to the door
- the *local server module* connected to the camera
- the *central server module* hosting face identification backend and authorization databases
- the *mobile application* providing on-the-go access controls

Combined, all of these modules ensure an end-to-end solution addressing needs of people.

## THe Embedded Module

The emedded module is an ESP32 microcontroller connected to a server motor. The servo motor opens and closes the door.

## The Local Server Module

The local server module is connected to a camera that keeps looking for faces. When at least one face is found, this module requests the central server to identify those faces. If they are identified, the embedded module is notified to open the door. Otherwise, the user receives a notification on their mobile device.

Facial recognition (distinguishing video frames containing faces from those missing faces) is done using YOLO v8.

## The Central Server Module

The central server module hosts the facial identification backend and the databases. Facial identification is done using insightface and a web-server is built using FatAPI. The database used for storing authentication data is MongoDB.

## The Mobile Application

The mobile application provides an easy way to modify the access to your home, right from your phone. This portable solution allows control over the faces you want to allow in your home. Further, homeowners will be notified on their mobile device if an unauthorized face is waiting at the door to be let in alongwith the ability to open the door for them or keep it closed.
