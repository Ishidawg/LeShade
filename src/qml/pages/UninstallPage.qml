import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.Page {
	title: qsTr("LeShade - Uninstall")

  ListModel {
    id: gameModel

    ListElement {
      title: "Shadow of the Colossus"
    }
    ListElement {
      title: "Demon's Souls"
    }
    ListElement {
      title: "Dark Souls REMASTERED"
    }
    ListElement {
      title: "Dragon's Dogma: Dark Arise"
    }
    ListElement {
      title: "Tales of Zestiria"
    }
    ListElement {
      title: "Farcry 1"
    }
    ListElement {
      title: "Furry GOTY 2027"
    }
    ListElement {
      title: "Demon's Crest"
    }
  }

  Component {
    id: gameDelegate

    Kirigami.AbstractCard {
      contentItem: Item {
        implicitWidth: delegateLayout.implicitWidth
        implicitHeight: delegateLayout.implicitHeight

        GridLayout {
          id: delegateLayout
          anchors {
            left: parent.left
            top: parent.top
            right: parent.right
          }

          rowSpacing: Kirigami.Units.largeSpacing
          columnSpacing: Kirigami.Units.largeSpacing
          columns: 2

          Kirigami.Heading {
            level: 2
            text: qsTr(title)
          }

          Controls.Button {
            Layout.alignment: Qt.AlignRight
					  icon.name: "user-trash-symbolic"
            text: qsTr("Uninstall")
          }
        }
      }
    }
  }

	Item {
		anchors.fill: parent

		ColumnLayout {
			// Fills horizontally only
			anchors.fill: parent
			anchors.verticalCenter: parent.verticalCenter

			Controls.Label {
				Layout.fillWidth: true
				Layout.alignment: Qt.AlignHCenter

				wrapMode: Text.WordWrap
				horizontalAlignment: Text.AlignHCenter

				text: qsTr("Games that you've installed ReShade on:")
      }

      Kirigami.CardsListView {
        id: gameCards

        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

        // Contains info to be displayed
        model: gameModel
        // Delegate hows the info will be presented in the ListView
        delegate: gameDelegate
      }

			RowLayout {
				Layout.alignment: Qt.AlignHCenter

				Controls.Button {
					icon.name: "user-home-symbolic"
          text: qsTr("Home")

					Controls.ToolTip.delay: 1000
					Controls.ToolTip.timeout: 5000
					Controls.ToolTip.visible: hovered
					Controls.ToolTip.text: qsTr("Returns to Home Page")

					onClicked: {
            applicationWindow().pageStack.replace(
              Qt.resolvedUrl("HomePage.qml")
            )
          }
				}
			}
		}
	}
}
