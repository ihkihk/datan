var storyView = new View();

storyView.butId = ['viz-story-button-1', 'viz-story-button-2', 'viz-story-button-3'];

storyView.create = function(d3c, ctrl)
{
	this.d3c = d3c;
	this.ctrl = ctrl;

	this.createButtonRibbon();
	this.createPages();
	
}; // end function create(...)
	
storyView.createButtonRibbon = function() {
	var width = getElementPropertyPx(this.d3c.nodes()[0].parentNode, 'width');

	var storyBtnW = 150, storyBtnH = 100, paddingBetweenBut = 250,
		ribbonLen = 3 * storyBtnW + 2 * paddingBetweenBut,
		ribbonOffsetFromView = (width - ribbonLen) / 2;

	var butCoords = [	{x: 0,                                 y: 0},
						{x: storyBtnW + paddingBetweenBut,     y: 0},
						{x: 2*(storyBtnW + paddingBetweenBut), y: 0}];

	var storyButtonsRibbon = this.d3c.append('g').
		attr('class', 'story-button-ribbon').
		attr('transform', 'translate(' + ribbonOffsetFromView + ', ' + 10 + ')');

	drawTextButton(storyButtonsRibbon,
		butCoords[0].x, butCoords[0].y, storyBtnW, storyBtnH, 
		'Which state takes highest loans', 'story-button', this.butId[0],
		function() { this.ctrl.selectPage(0); }.bind(this));

	drawTextButton(storyButtonsRibbon,
		butCoords[1].x, butCoords[1].y, storyBtnW, storyBtnH,
		'Which profession takes highest loans', 'story-button', this.butId[1],
		function() { this.ctrl.selectPage(1); }.bind(this));

	drawTextButton(storyButtonsRibbon,
		butCoords[2].x, butCoords[2].y, storyBtnW, storyBtnH,
		'Which people default on their loans', 'story-button', this.butId[2],
		function() { this.ctrl.selectPage(2); }.bind(this));
}; // end function createButtonRibbon(...)
	
storyView.setButtonState = function(butNo, flState) {
	this.butId.forEach(function(b) { d3.select("#" + b).classed('clicked', false); });
	
	d3.select("#" + this.butId[butNo]).classed('clicked', flState);
};
	
storyView.createPages = function() {
	// Create a canvas that will house the overlapping story pages
	var canvas = this.d3c.append('g').
		attr('transform', 'translate(0,150)');
		
	this.ctrl.pageCtrl[0].createView(canvas, this.ctrl, flShow=false);
	this.ctrl.pageCtrl[1].createView(canvas, this.ctrl, flShow=false);
	this.ctrl.pageCtrl[2].createView(canvas, this.ctrl, flShow=false);
	
	this.ctrl.configPages();
};

var storyCtrl = {
	view: storyView,
	pageCtrl: [page0Ctrl, page1Ctrl, page2Ctrl],
	parentCtrl: null,

	selectPage: function(pageNo) {
		this.pageCtrl.forEach(function(p) { p.show(false); });
		this.pageCtrl[pageNo].show(true);
		this.view.setButtonState(pageNo, true);
	},
	
	
	configPages: function() {
		this.pageCtrl[0].show(true);
		this.view.setButtonState(0, true);
	},

	createView: function(d3c, parentCtrl) {
		this.parentCtrl = parentCtrl;
		this.view.create(d3c, this);
	}
};