(function () {
  function init() {

    // Since 2.2 you can also author concise templates with method chaining instead of GraphObject.make
    // For details, see https://gojs.net/latest/intro/buildingObjects.html
    const $ = go.GraphObject.make;

    myDiagram =
      $(go.Diagram, "myDiagramDiv",
        {
          initialContentAlignment: go.Spot.Left,
          initialAutoScale: go.Diagram.UniformToFill,
          layout: $(go.LayeredDigraphLayout,
            { direction: 0, alignOption: go.LayeredDigraphLayout.AlignAll }),
          "undoManager.isEnabled": true
        }
      );

    function makePort(name, leftside) {
      var port = $(go.Shape, "Rectangle",
        {
          fill: "gray", stroke: null,
          desiredSize: new go.Size(8, 8),
          portId: name,  // declare this object to be a "port"
          toMaxLinks: 1,  // don't allow more than one link into a port
          fromMaxLinks: 1,  // don't allow more than one link from a port
          cursor: "pointer"  // show a different cursor to indicate potential link point
        });

      var lab = $(go.TextBlock, name,  // the name of the port
        { font: "7pt sans-serif" });

      var panel = $(go.Panel, "Horizontal",
        { margin: new go.Margin(2, 0) });

      // set up the port/panel based on which side of the node it will be on
      if (leftside) {
        port.toSpot = go.Spot.Left;
        port.toLinkable = true;
        lab.margin = new go.Margin(1, 0, 0, 1);
        panel.alignment = go.Spot.TopLeft;
        panel.add(port);
        panel.add(lab);
      } else {
        port.fromSpot = go.Spot.Right;
        port.fromLinkable = true;
        lab.margin = new go.Margin(1, 1, 0, 0);
        panel.alignment = go.Spot.TopRight;
        panel.add(lab);
        panel.add(port);
      }
      return panel;
    }
    function textStyle() {
      return { font: "9pt  Segoe UI,sans-serif", stroke: "white" };
    }

    function addMetaData(addMData, isBuffer, cycleTimeOnly) {
      if (!addMData) {
        return {};
      }
      if (isBuffer) {
        return $(go.Panel, "Vertical", { row: 3 },
          $(go.Panel, "Horizontal",
            // property name, underlined if scope=="class" to indicate static property
            $(go.TextBlock, "Capacity: ", textStyle(),
              { row: 1, column: 0 }),
            // property type, if known
            $(go.TextBlock,
              { isMultiline: false, editable: true },
              new go.Binding("text", "capacity").makeTwoWay()),
          ),
        )
      }
      if (cycleTimeOnly) {
        return $(go.Panel, "Vertical", { row: 3 },
          $(go.Panel, "Horizontal",
            // property name, underlined if scope=="class" to indicate static property
            $(go.TextBlock, "Cycle Time: ", textStyle(),
              { row: 1, column: 0 }),
            // property type, if known
            $(go.TextBlock,
              { isMultiline: false, editable: true },
              new go.Binding("text", "ct").makeTwoWay()),
          )
        )
      }
      return $(go.Panel, "Vertical", { row: 3 },
        $(go.Panel, "Horizontal",
          // property name, underlined if scope=="class" to indicate static property
          $(go.TextBlock, "Cycle Time: ", textStyle(),
            { row: 1, column: 0 }),
          // property type, if known
          $(go.TextBlock,
            { isMultiline: false, editable: true },
            new go.Binding("text", "ct").makeTwoWay()),
        ),
        $(go.Panel, "Horizontal",
          // property name, underlined if scope=="class" to indicate static property
          $(go.TextBlock, "MTTR: ", textStyle(),
            { row: 1, column: 0 }),
          // property type, if known
          $(go.TextBlock,
            { isMultiline: false, editable: true },
            new go.Binding("text", "mttr").makeTwoWay()),
        ),
        $(go.Panel, "Horizontal",
          // property name, underlined if scope=="class" to indicate static property
          $(go.TextBlock, "MTBF: ", textStyle(),
            { row: 1, column: 0 }),
          // property type, if known
          $(go.TextBlock,
            { isMultiline: false, editable: true },
            new go.Binding("text", "mtbf").makeTwoWay()),
        )
      );
    }

    function makeTemplate(typename, background, inports, outports, isBuffer = false, cycleTimeOnly = false, addMData = true) {
      var node = $(go.Node, "Spot",
        $(go.Panel, "Auto",
          {
            width: 140, height: 120,
            doubleClick: showSettingsDrawer
          },
          $(go.Shape, "Rectangle",
            {
              fill: background, stroke: null, strokeWidth: 0,
              spot1: go.Spot.TopLeft, spot2: go.Spot.BottomRight
            }),
          $(go.Panel, "Table",
            $(go.TextBlock,
              new go.Binding("text", "key"),
              {
                row: 0,
                margin: 3,
                maxSize: new go.Size(80, NaN),
                stroke: "black",
                font: "bold 10pt sans-serif"
              }),
            addMetaData(addMData, isBuffer, cycleTimeOnly)
          ),
        ),
        $(go.Panel, "Vertical",
          {
            alignment: go.Spot.Left,
            alignmentFocus: new go.Spot(0, 0.5, 8, 0)
          },
          inports),
        $(go.Panel, "Vertical",
          {
            alignment: go.Spot.Right,
            alignmentFocus: new go.Spot(1, 0.5, -8, 0)
          },
          outports)
      );
      myDiagram.nodeTemplateMap.set(typename, node);
    }

    makeTemplate("Source", "forestgreen",
      [],
      [makePort("OUT", false)], false, true, false);

    makeTemplate("Sink", "red",
      [makePort("IN", true)],
      [], false, true, false);

    makeTemplate("Process", "lightblue",
      [makePort("IN", true)],
      [makePort("OUT", false)]);

    makeTemplate("Combinor", "blue",
      [makePort("IN1", true), makePort("IN2", true)],
      [makePort("OUT", false)], false, true, false);

    makeTemplate("Separator", "blue",
      [makePort("IN", true)],
      [makePort("OUT1", false), makePort("OUT2", false)], false, true, false);

    makeTemplate("Buffer", "grey",
      [makePort("IN", true)],
      [makePort("OUT", false)], true);

    myDiagram.linkTemplate =
      $(go.Link,
        {
          routing: go.Link.Orthogonal, corner: 25,
          relinkableFrom: true, relinkableTo: true
        },
        $(go.Shape, { stroke: "gray", strokeWidth: 2 }),
        $(go.Shape, { stroke: "gray", fill: "gray", toArrow: "Standard" })
      );

    load({
      "class": "go.GraphLinksModel",
      "nodeCategoryProperty": "type",
      "linkFromPortIdProperty": "frompid",
      "linkToPortIdProperty": "topid",
      "nodeDataArray": [],
      "linkDataArray": []
    });

    // initialize the Palette that is on the left side of the page
    myPalette =
      $(go.Palette, "myPaletteDiv",  // must name or refer to the DIV HTML element
        {
          maxSelectionCount: 1,
          nodeTemplateMap: myDiagram.nodeTemplateMap,  // share the templates used by myDiagram
          model: go.Model.fromJson(
            {
              "class": "go.GraphLinksModel",
              "nodeCategoryProperty": "type",
              "linkFromPortIdProperty": "frompid",
              "linkToPortIdProperty": "topid",
              "nodeDataArray": [
                { "key": "Buffer", "type": "Buffer", "capacity": "10" },
                { "key": "Source", "type": "Source" },
                { "key": "Sink", "type": "Sink" },
                { "key": "Process", "type": "Process", "ct": "10", "ttr_dist": { "type": "EXPONENTIAL", "params": { "mean": "10" } }, "tbf_dist": { "type": "EXPONENTIAL", "params": { "mean": "10" } } },
                { "key": "Combinor", "type": "Combinor" },
                { "key": "Separator", "type": "Separator" }
              ],
              "linkDataArray": []
            })
        });

    // Show the diagram's model in JSON format that the user may edit
    function save() {
      var file = new Blob([myDiagram.model.toJson()], { type: 'text/plain' });
      var a = document.createElement("a"),
        url = URL.createObjectURL(file);
      a.href = url;
      a.download = "model.json";
      document.body.appendChild(a);
      a.click();
      setTimeout(function () {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }, 0);
    }
    function keyGenerator(model, data) {
      // Increment id up for each type
      index = 0;
      for (var i = 0; i < model.nodeDataArray.length; i++) {
        if (model.nodeDataArray[i].type == data.type) {
          index += 1;
        }
      }
      data.key = data.type + " " + String(index + 1);
      return data.key;
    }
    function load(model_json) {
      myDiagram.model = go.Model.fromJson(model_json);
      myDiagram.model.makeUniqueKeyFunction = keyGenerator;
      myDiagram.model.copyNodeDataFunction = function (data, model) {
        var newdata = Object.assign({}, data);
        newdata.key = keyGenerator(model, newdata);
        return newdata;
      };
    }

    document.getElementById("SaveButton").onclick = save;

    function sendModelToBackend() {
      // Generate JavaScript code and display it.
      var model = myDiagram.model.toJson();
      document.getElementById("simulationRunningText").style.display = "block";
      fetch('/simulate', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "model": model, "simulation_time": document.getElementById("SimulationTime").value })
      }).then(response => response.json())
        .then((output) => {
          document.getElementById("SimulationResults").value = JSON.stringify(output["output"], null, 4);
          document.getElementById("simulationRunningText").style.display = "none";
        })
    }
    document.getElementById("SendModel").onclick = sendModelToBackend;

    const fileSelector = document.getElementById('FileSelector');
    fileSelector.addEventListener('change', (event) => {
      const fileList = event.target.files;
      let fr = new FileReader();
      fr.onload = (e) => load(e.target.result);
      fr.readAsText(fileList[0]);
    });
  }
  window.addEventListener('DOMContentLoaded', init);
})();
