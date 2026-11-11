import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "pages"
import "components"

// Notes:
// anchors = relative position, so it difines position relative to the parent. use to position Layouts
// Layout = organize elements inside a structure. Use to position elements.
// Width = default on every item, do not use in layouts
// Layout.prefferedWidth = target size of an item (if it have width enough)

// Provides basic features needed for all kirigami applications
Kirigami.ApplicationWindow {
  // Unique identifier to reference this object
  id: root
  minimumWidth: 620
	minimumHeight: 500
	width: 620
	height: 500

	title: "LeShade 2.6.0"

  // Set the first page that will be loaded when the app opens
	// This can also be set to an id of a Kirigami.Page
	pageStack.initialPage: HomePage {}

	// GlobalToolBar Styling - remove navigation buttons, adjust height and leaves title
	pageStack.globalToolBar.style: Kirigami.ApplicationHeaderStyle.Titles
	pageStack.globalToolBar.showNavigationButtons: Kirigami.ApplicationHeaderStyle.NoNavigationButtons
	pageStack.globalToolBar.preferredHeight: Kirigami.Units.largeSpacing * 5

	footer: Footer {}
}
