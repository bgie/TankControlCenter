import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtGraphicalEffects 1.12

ApplicationWindow {
    id: window
    title: header.text
    width: 1200
    height: 800
    visible: true
    visibility: Qt.WindowFullScreen
    flags: Qt.FramelessWindowHint | Qt.Window

    background: Rectangle {
        color:  "#101010"
    }

    Timer {
        interval: 1;
        running: true;
        repeat: true
        onTriggered: {
            Joysticks.refresh();
            RemoteControl.discover();
        }
    }


    Text {
        id: header
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.bottomMargin: 40
        text: "Maaktank Controlecentrum"
        font.pixelSize: 64
        color: "#E0F0FF"
    }

    Item {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: parent.bottom

        Row {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: parent.height / 2

            Repeater {
                model: Tanks

                Item {
                    id: tank
                    width: parent.width / 3
                    height: parent.height
                    property bool connected: RemoteControl.connected(index+1)

                    Rectangle {
                        id: tankContent
                        anchors.fill: parent
                        anchors.margins: 20
                        color: "#FFFFFF"
                        border.color: "#000000"
                        border.width: 3
                        radius: 30

                        Rectangle  {
                            id: tankImage
                            anchors.centerIn: parent
                            height: 100
                            width: 300

                            Image {
                                anchors.fill: parent
                                source: "tank.png"
                            }
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: tankImage.top
                            anchors.bottomMargin: 20
                            text: "Tank " + (index+1)
                            font.pixelSize: 48
                            color: "#000000"
                        }
                    }

                    ColorOverlay {
                        anchors.fill: tankContent
                        source: tankContent
                        color: "#F0101010"
                        visible: !tank.connected
                    }

                    Connections {
                        target: RemoteControl
                        function onDiscovered() {
                            tank.connected = RemoteControl.connected(index+1);
                        }
                    }
                }
            }
        }


        Row {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: parent.height / 2

            Repeater {
                model: Tanks

                Item {
                    id: gamepad
                    width: parent.width / 3
                    height: parent.height
                    property bool connected: Joysticks.connected(index+1)

                    Rectangle {
                        id: gamepadContent
                        anchors.fill: parent
                        anchors.margins: 20
                        anchors.bottomMargin: 40
                        color: "#FFFFFF"
                        border.color: "#000000"
                        border.width: 3
                        radius: 30

                        Rectangle  {
                            id: gamepadImage
                            anchors.centerIn: parent
                            height: 200
                            width: 300

                            Image {
                                anchors.fill: parent
                                source: "gamepad.png"
                            }
                        }

                        Text {
                            id: player
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: gamepadImage.bottom
                            text: "Speler " + (index+1)
                            font.pixelSize: 48
                            color: "#000000"
                        }

                        Text {
                            id: debug
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 10
                        }
                    }

                    ColorOverlay {
                        anchors.fill: gamepadContent
                        source: gamepadContent
                        color: "#F0101010"
                        visible: !gamepad.connected
                    }

                    Connections {
                        target: Joysticks
                        function onRefreshed() {
                            var connected = Joysticks.connected(index+1);
                            gamepad.connected = connected;
                            if(connected) {
                                debug.text = Joysticks.buttons(index+1).toString(2) + " " +
                                    Joysticks.x(index+1).toString() + " " +
                                    Joysticks.y(index+1).toString();
                            }
                            else {
                                debug.text = ""
                            }
                        }
                    }
                }
            }
        }

    }

    Button {
        id: closeButton
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 20
        width: 32
        height: 32
        background: Item {}
        onClicked: window.close()

        Image {
            visible: closeButton.hovered
            anchors.fill: parent
            source: "close-button.png"
        }
        Image {
            visible: !closeButton.hovered
            anchors.fill: parent
            source: "close-button-grayed.png"
        }
    }

    Text {
        id: refreshesPerSecond
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 5
        color: "#707070"

        Timer {
            interval: 1000;
            running: true;
            repeat: true
            onTriggered: refreshesPerSecond.text = "Joystick latency: " + (1000 / Joysticks.refreshesPerSecond()).toFixed(2) + "ms"
        }
    }
}
