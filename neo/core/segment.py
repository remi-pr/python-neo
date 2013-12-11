from neo.core.baseneo import BaseNeo

import numpy as np


class Segment(BaseNeo):
    """
    A Segment is a heterogeneous container for discrete or continous data
    sharing a common clock (time basis) but not necessary the same sampling
    rate, start or end time.

    *Usage*:

    TODO

    *Required attributes/properties*:
        None

    *Recommended attributes/properties*:
        :name: A label for the dataset
        :description: text description
        :file_origin: filesystem path or URL of the original data file.
        :file_datetime: the creation date and time of the original data file.
        :rec_datetime: the date and time of the original recording
        :index: integer. You can use this to define a temporal ordering of
            your Segment. For instance you could use this for trial numbers.

    *Container of*:
        :py:class:`Epoch`
        :py:class:`EpochArray`
        :py:class:`Event`
        :py:class:`EventArray`
        :py:class:`AnalogSignal`
        :py:class:`AnalogSignalArray`
        :py:class:`IrregularlySampledSignal`
        :py:class:`Spike`
        :py:class:`SpikeTrain`

    """
    def __init__(self, name=None, description=None, file_origin=None,
                 file_datetime=None, rec_datetime=None, index=None,
                 **annotations):
        BaseNeo.__init__(self, name=name, file_origin=file_origin,
                         description=description, **annotations)
        self.file_datetime = file_datetime
        self.rec_datetime = rec_datetime
        self.index = index

        self.epochs = []
        self.epocharrays = []
        self.events = []
        self.eventarrays = []
        self.analogsignals = []
        self.analogsignalarrays = []
        self.irregularlysampledsignals = []
        self.spikes = []
        self.spiketrains = []

        self.block = None

    @property
    def all_data(self):
        return sum((self.epochs, self.epocharrays, self.events,
                    self.eventarrays, self.analogsignals,
                    self.analogsignalarrays, self.irregularlysampledsignals,
                    self.spikes, self.spiketrains), [])

    def filter(self, **kwargs):
        """
        Return a list of data objects matching *any* of the search terms
        in either their attributes or annotations.

        Examples::

            >>> segment.filter(name="Vm")
        """
        results = []
        for key, value in kwargs.items():
            for obj in self.all_data:
                if hasattr(obj, key) and getattr(obj, key) == value:
                    results.append(obj)
                elif key in obj.annotations and obj.annotations[key] == value:
                    results.append(obj)
        return results

    def take_spikes_by_unit(self, unit_list=None):
        '''
        Return Spikes in the segment that are also in a unit in the list
        of units provided
        '''
        if unit_list is None:
            return []
        spike_list = []
        for spike in self.spikes:
            if spike.unit in unit_list:
                spike_list.append(spike)
        return spike_list

    def take_spiketrains_by_unit(self, unit_list=None):
        '''
        Return SpikeTrains in the segment that are also in a unit in the list
        of units provided
        '''
        if unit_list is None:
            return []
        spiketrain_list = []
        for spiketrain in self.spiketrains:
            if spiketrain.unit in unit_list:
                spiketrain_list.append(spiketrain)
        return spiketrain_list

    def take_analogsignal_by_unit(self, unit_list=None):
        '''
        Return AnalogSignals in the segment that are from the same
        channel_index as the units provided.
        '''
        if unit_list is None:
            return []
        channel_indexes = []
        for unit in unit_list:
            if unit.channel_indexes is not None:
                channel_indexes.extend(unit.channel_indexes)
        return self.take_analogsignal_by_channelindex(channel_indexes)

    def take_analogsignal_by_channelindex(self, channel_indexes=None):
        '''
        Return AnalogSignals in the segment that have a channel_index
        that is in the list indexes provided.
        '''
        if channel_indexes is None:
            return []
        anasig_list = []
        for anasig in self.analogsignals:
            if anasig.channel_index in channel_indexes:
                anasig_list.append(anasig)
        return anasig_list

    def take_slice_of_analogsignalarray_by_unit(self, unit_list=None):
        '''
        Return slices of the AnalogSignalArrays in the segment that correspond
        to the same channe_indexes as the units provided.
        '''
        if unit_list is None:
            return []
        indexes = []
        for unit in unit_list:
            if unit.channel_indexes is not None:
                indexes.extend(unit.channel_indexes)

        return self.take_slice_of_analogsignalarray_by_channelindex(indexes)

    def take_slice_of_analogsignalarray_by_channelindex(self,
                                                        channel_indexes=None):
        '''
        Return slices of the AnalogSignalArrays in the segment that correspond
        to the channe_indexes provided.
        '''
        if channel_indexes is None:
            return []

        sliced_sigarrays = []
        for sigarr in self.analogsignalarrays:
            if sigarr.channel_indexes is not None:
                ind = np.in1d(sigarr.channel_indexes, channel_indexes)
                sliced_sigarrays.append(sigarr[:, ind])

        return sliced_sigarrays

    def construct_subsegment_by_unit(self, unit_list=None):
        """
        Return AnalogSignal list in a given segment given there Unit parents.

        *Example*::

            # construction
            nb_seg = 3
            nb_unit = 5
            unit_with_sig = [0, 2, 3]
            signal_types = ['Vm', 'Conductances']

            #recordingchannelgroups
            rcgs = [ RecordingChannelGroup(name = 'Vm',
                                           channel_indexes = unit_with_sig),
                            RecordingChannelGroup(name = 'Conductance',
                                                  channel_indexes =
                                                  unit_with_sig), ]

            # Unit
            all_unit = [ ]
            for u in range(nb_unit):
                un = Unit(name = 'Unit #{}'.format(j), channel_index = u)
                all_unit.append(un)

            bl = block()
            for s in range(nb_seg):
                seg = Segment(name = 'Simulation {}'.format(s))
                for j in range(nb_unit):
                    st = SpikeTrain([1, 2, 3], units = 'ms', t_start = 0.,
                                    t_stop = 10)
                    st.unit = all_unit[j]

                for t in signal_types:
                    anasigarr = AnalogSignalArray( zeros(10000,
                                                         len(unit_with_sig) ))

        """
        seg = Segment()
        seg.analogsignals = self.take_analogsignal_by_unit(unit_list)
        seg.spiketrains = self.take_spiketrains_by_unit(unit_list)
        seg.analogsignalarrays = \
            self.take_slice_of_analogsignalarray_by_unit(unit_list)
        #TODO copy others attributes
        return seg

    def merge(self, other):
        """
        Merge the contents of another segment into this one.

        For each array-type object in the other segment, if its name matches
        that of an object of the same type in this segment, the two arrays
        will be joined by concatenation. Non-array objects will just be added
        to this segment.
        """
        for container in ("epochs",  "events",  "analogsignals",
                          "irregularlysampledsignals", "spikes",
                          "spiketrains"):
            getattr(self, container).extend(getattr(other, container))
        for container in ("epocharrays", "eventarrays", "analogsignalarrays"):
            objs = getattr(self, container)
            lookup = dict((obj.name, i) for i, obj in enumerate(objs))
            for obj in getattr(other, container):
                if obj.name in lookup:
                    ind = lookup[obj.name]
                    try:
                        newobj = getattr(self, container)[ind].merge(obj)
                    except AttributeError as e:
                        raise AttributeError("%s. container=%s, obj.name=%s, \
                                              shape=%s" % (e, container,
                                                           obj.name,
                                                           obj.shape))
                    getattr(self, container)[ind] = newobj
                else:
                    lookup[obj.name] = obj
                    getattr(self, container).append(obj)
        # TODO: merge annotations

    def size(self):
        return dict((name, len(getattr(self, name)))
                    for name in ("epochs",  "events",  "analogsignals",
                                 "irregularlysampledsignals", "spikes",
                                 "spiketrains", "epocharrays", "eventarrays",
                                 "analogsignalarrays"))

    def _repr_pretty_(self, pp, cycle):
        pp.text(self.__class__.__name__)
        pp.text(" with ")
        first = True
        for (value, readable) in [
                (self.analogsignals, "analogs"),
                (self.analogsignalarrays, "analog arrays"),
                (self.events, "events"),
                (self.eventarrays, "event arrays"),
                (self.epochs, "epochs"),
                (self.epocharrays, "epoch arrays"),
                (self.irregularlysampledsignals, "epoch arrays"),
                (self.spikes, "spikes"),
                (self.spiketrains, "spike trains"),
                ]:
            if value:
                if first:
                    first = False
                else:
                    pp.text(", ")
                pp.text("{0} {1}".format(len(value), readable))
        if self._has_repr_pretty_attrs_():
            pp.breakable()
            self._repr_pretty_attrs_(pp, cycle)

        if self.analogsignals:
            pp.breakable()
            pp.text("# Analog signals (N={0})".format(len(self.analogsignals)))
            for (i, asig) in enumerate(self.analogsignals):
                pp.breakable()
                pp.text("{0}: ".format(i))
                with pp.indent(3):
                    pp.pretty(asig)

        if self.analogsignalarrays:
            pp.breakable()
            pp.text("# Analog signal arrays (N={0})"
                    .format(len(self.analogsignalarrays)))
            for i, asarr in enumerate(self.analogsignalarrays):
                pp.breakable()
                pp.text("{0}: ".format(i))
                with pp.indent(3):
                    pp.pretty(asarr)
