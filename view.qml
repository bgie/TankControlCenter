import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Window 2.15
import QtGraphicalEffects 1.12

ApplicationWindow {
    id: window
    title: "Controle Centrum"
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

    property color glowingRed;
    SequentialAnimation on glowingRed {
        loops: Animation.Infinite
        ColorAnimation {
            from: "#7F0000"
            to: "#FF0000"
            duration: 500
        }
        ColorAnimation {
            from: "#FF0000"
            to: "#7F0000"
            duration: 500
        }
    }
    property color tankImageBackgroundColor: "#DBD2CD"

    Item {
        id: header
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.right: parent.right
        height: 20
    }

    Item {
        id: content
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: parent.bottom

        Grid {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: parent.height

            columns: TankColumns
            rows: TankRows

            Repeater {
                model: Tanks

                Item {
                    id: tankItem
                    width: parent.width / parent.columns
                    height: parent.height / parent.rows

                    Rectangle {
                        id: tankContent
                        anchors.fill: parent
                        anchors.margins: 20
                        color: tankImageBackgroundColor
                        border.color: "#000000"
                        border.width: 3
                        radius: 30

                        Image  {
                            id: tankImage
                            anchors.centerIn: parent
                            source: "img/tank.png"
                            fillMode: Image.PreserveAspectFit
                            width: parent.width * 0.8
                            height: parent.height * 0.8
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 20
                            text: modelData.name
                            font.pixelSize: 48
                            color: "#000000"
                        }

                        Image  {
                            id: gamepadImage
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.margins: 20
                            source: "img/gamepad.png"
                            opacity: 0
                            width: sourceSize.width
                            height: sourceSize.height

                            states: State {
                                name: "assigned"
                                when: modelData.joystickAssigned
                                PropertyChanges { target: gamepadImage; opacity: 1 }
                                PropertyChanges { target: gamepadImage; width: sourceSize.width * 0.2 }
                                PropertyChanges { target: gamepadImage; height: sourceSize.height * 0.2 }
                            }
                            transitions: Transition {
                                PropertyAnimation { properties: "opacity"; duration: 50 }
                                PropertyAnimation { properties: "width, height"; duration: 300 }
                            }
                        }
                    }

                    ColorOverlay {
                        id: disabledTankOverlay
                        anchors.fill: tankContent
                        source: tankContent
                        color: "#E7101010"
                        visible: !modelData.connected
                    }

                    Rectangle {
                        id: tankSelection
                        anchors.fill: parent
                        anchors.margins: 20
                        color: "transparent"
                        border.width: 15
                        radius: 30
                        border.color: window.glowingRed

                        Text {
                            anchors.centerIn: parent
                            text: "DRUK START"
                            font {
                                pixelSize: 96
                                bold: true
                            }
                            style: Text.Outline
                            styleColor: disabledTankOverlay.visible ? "#000000" : tankImageBackgroundColor
                            color: window.glowingRed
                        }
                    }

                    Positioner.onIndexChanged: {
                        var box = TankSelection.box_at_index(tankItem.Positioner.index)
                        tankSelection.visible = Qt.binding(function() { return box.selected })
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
            source: "img/close-button.png"
        }
        Image {
            visible: !closeButton.hovered
            anchors.fill: parent
            source: "img/close-button-grayed.png"
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

    Image {
        anchors.centerIn: content
        visible: RemoteControl && !RemoteControl.connected
        source: "img/disconnected.png"
    }
}
