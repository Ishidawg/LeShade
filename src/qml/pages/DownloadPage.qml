import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.Page {
  title: "LeShade - Download ReShade"

  Item {
			anchors.fill: parent
    ColumnLayout {
      anchors.verticalCenter: parent.verticalCenter
      anchors.left: parent.left
      anchors.right: parent.right

      spacing: 20

      Controls.Label {
        Layout.maximumWidth: 800
				Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter

				wrapMode: Text.WordWrap
				horizontalAlignment: Text.AlignJustify
     
				topPadding: Kirigami.Units.largeSpacing * 4
				bottomPadding: Kirigami.Units.largeSpacing * 2

        // text: qsTr("You can select if ReShade has addon support or not, and choose the version. Do not use addon support for multiplayer games with anti-cheat.")
        text: qsTr("Here you choose what version of ReShade you want to install: Addon or non-addon support. Select the ReShade release version too (nightly to have the latest one). Keep in mind that is recommended to not use addon support for multiplayer games with anti-cheat.")
      }

      ColumnLayout {
        Layout.alignment: Qt.AlignHCenter
        Layout.maximumWidth: 800
        Layout.fillHeight: true
        
        spacing: 12

        RowLayout {
				  Layout.fillWidth: true
          Controls.ComboBox {
            Layout.fillWidth: true
            model: ListModel {
              id: versionModel
              ListElement { text: qsTr("addon")}
              ListElement { text: qsTr("non-addon")}
            }
          }
          Controls.ComboBox {
            Layout.fillWidth: true
            model: ListModel {
              id: releaseModel
              ListElement { text: qsTr("7.5.1")}
              ListElement { text: qsTr("7.5.0")}
            }
          }
        }
        Controls.Button {
				  Layout.fillWidth: true
          text: qsTr("Download")
        }
        Controls.ProgressBar {
				  Layout.fillWidth: true
          value: 50.0
        }
      }
    }
  }
}
