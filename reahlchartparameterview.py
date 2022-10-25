
from reahl.web.fw import UserInterface, UrlBoundView
from reahl.web.ui import HTML5Page, HTMLWidget
from reahl.web.plotly import Chart
from reahl.web.layout import PageLayout
from reahl.web.bootstrap.ui import Div, H, P, A, Br
from reahl.web.bootstrap.grid import Container, ColumnLayout, ColumnOptions, ResponsiveSize
from reahl.web.bootstrap.navbar import Navbar, ResponsiveLayout
from reahl.web.bootstrap.navs import Nav
from reahl.web.bootstrap.popups import PopupA
from reahl.web.bootstrap.forms import Form, FormLayout, SelectInput
from reahl.component.modelinterface import exposed, Field, ChoiceField, Choice, IntegerField

import plotly.graph_objects as go

class DefaultPage(HTML5Page):
    def __init__(self, view):
        super().__init__(view)

        self.use_layout(PageLayout(document_layout=Container()))
        contents_layout = ColumnLayout(ColumnOptions('main', size=ResponsiveSize())).with_slots()
        self.layout.contents.use_layout(contents_layout)


class MySitePage(DefaultPage):
    def __init__(self, view):
        super().__init__(view)

        #add some Navbar etc...


class GraphView(UrlBoundView):
    def assemble(self, my_record_key=None):
        #Be sure not to use actual db record ids: https://security.stackexchange.com/questions/258511/uuids-replacing-inremental-ids-in-urls
        self.title = 'Graph %s' % my_record_key
        self.set_slot('main', MyGraphWidget.factory(my_record_key=my_record_key))


class MyGraphWidget(HTMLWidget):
    def __init__(self, view, my_record_key=None):
        super(MyGraphWidget, self).__init__(view)
        #Do something with db to get data for my_record_key

        fig = self.create_plotly_figure()
        self.add_child(Chart(view, fig, 'mychart'))


    def create_plotly_figure(self):

        france_peaks = [2750, 2217, 2082, 4102, 4808]
        height_rank_bins = ['5', '4', '3', '2', '1']
        south_africa_peaks = [-1 * i for i in [3375, 3377, 3410, 3451, 3455]]
        other_country_peaks = france_peaks

        fig = go.Figure()
        fig.add_trace(go.Bar(y=height_rank_bins, x=other_country_peaks,
                             name='France', orientation='h'))
        fig.add_trace(go.Bar(y=height_rank_bins, x=south_africa_peaks,
                             name='South Africa', orientation='h'))

        fig.update_layout(
            title='Peak Elevation Pyramid',
            barmode='relative',
            bargap=0.1,
            bargroupgap=0,
            xaxis=dict(tickvals=[-4000, -3000, -2000, 0, 2000, 3000, 4000],
                       ticktext=['4,000m', '3,000m', '2,000m', '0m',
                                 '2,000m', '3,000m', '4,000m'],
                       title='Peak elevation')
        )

        return fig


class MyRecordsPanel(Div):
    def __init__(self, view, ui, graph_view):
        super().__init__(view)

        self.add_child(H(view, 1, text='My records'))

        for my_record_key in [1, 2, 3, 4, 5]:
            bookmark = graph_view.as_bookmark(ui, my_record_key=my_record_key)
            self.add_child(A.from_bookmark(self.view, bookmark))
            self.add_child(Br(view))
            # popups only load contents for an id - we actually need the whole page...
            # content_to_show_id = '#mychart'
            # self.add_child(PopupA(view, bookmark, content_to_show_id))


class MyUI(UserInterface):
    def assemble(self):
        home = self.define_view('/', title='Home', page=MySitePage.factory())
        graph_view = self.define_view('/graph', page=DefaultPage.factory(), view_class=GraphView, my_record_key=Field(required=True))

        home.set_slot('main', MyRecordsPanel.factory(self, graph_view))
