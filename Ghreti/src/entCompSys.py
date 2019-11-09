import time as _t
from functools import lru_cache as lruc

class System:
    attached = None
    def process(self, *args,**kwargs):
        raise NotImplementedError


class World:
    def __init__(self, timed=False):
        self.systems = []
        self.nextEntityId = 0
        self.components = {}
        self.entities = {}
        self.deadEntities = set()
        if timed:
            self.processTimes = {}
            self.process = self.timedProcess

    def clearCache(self):
        self.getComponent.cache_clear() #lru_cache related
        self.getComponents.cache_clear()

    def clearDatabase(self):
        self.nextEntityId = 0
        self.deadEntities.clear()
        self.components.clear()
        self.entities.clear()
        self.clearCache()

    def addSystem(self,sys,priority=0):
        assert issubclass(sys.__class__,System)
        sys.priority = priority
        sys.attached = self
        self.systems.append(sys)
        self.systems.sort(key=lambda s: s.priority,reverse=True)

    def removeSystem(self,sys):
        for system in self.systems:
            if isinstance(sys,system):
                sys.attached = None
                self.systems.remove(sys)

    def getSystem(self,sys):
        for system in self.systems:
            if isinstance(sys,system):
                return sys

    def createEntity(self,*components):
        self.nextEntityId += 1
        for c in components:
            self.addComponent(self.nextEntityId,c)
        return self.nextEntityId

    def deleteEntity(self,ent,now=False):
        if now:
            for comp in self.entities[ent]:
                self.components[comp].discard(ent)
                if not self.components[comp]:
                    del self.components[comp]
            del self.entities[ent]
            self.clearCache()
        else:
            self.deadEntities.add(ent)

    def componentForEntity(self,ent,comp):
        return self.entities[ent][comp]

    def componentsForEntity(self,ent):
        return tuple(self.entities[ent].values())

    def hasComponent(self,ent, comp):
        return comp in self.entities[ent]

    def addComponent(self,ent,comp):
        compType = type(comp)
        if compType not in self.components:
            self.components[compType] = set()
        self.components[compType].add(ent)
        if ent not in self.entities:
            self.entities[ent] = {}
        self.entities[ent][compType] = comp
        self.clearCache()

    def removeComponent(self,ent,comp):
        self.components[comp].discard(ent)
        if not self.components[comp]:
            del self.components[comp]
        del self.entities[ent][comp]
        if not self.entities[ent]:
            del self.entities[ent]
        self.clearCache()
        return ent

# not for public consumption
    def _getComponent(self,comp):
        edb = self.Entities #database
        for ent in self.components.get(comp,[]):
            yield ent, edb[ent][comp]

    def _getComponents(self,*comps):
        edb = self.entities
        cdb = self.components
        try:
            for e in set.intersection(*[cdb[c] for c in comps]):
                yield e, [edb[e][c] for c in comps]
        except KeyError:
            pass
# this is the public interface portion using the lruc() decorator
# for handling the cache, least recently used cache
    @lruc()
    def getComponent(self,comp):
        return [c for c in self._getComponent(comp)]

    @lruc()
    def getComponents(self, *comps):
        return [c for c in self._getComponents(*comps)]

    def tryComponent(self, ent, comp):
        if comp in self.entities[ent]:
            yield self.entities[ent][comp]
        else:
            return None

    def clearDeadEntities(self):
        for e in self.deadEntities:
            for c in self.entities[e]:
                self.components[c].discard(e)
                if not self.components[c]:
                    del self.components[c]
            del self.entities[e]
        self.entities.clear()
        self.clearCache()

    def _process(self, *args, **kwargs):
        for s in self.systems:
            s.process(*arg,**kwargs)

    def _timedProcess(self,*args,**kwargs):
        for s in self.systems:
            st = _t.process_time()
            s.process(*args,**kwargs)
            processTime = int(round((_time.process_time()-st)*1000, 2))
            self.processTimes[s.__class__.__name__] = processTime

    def process(self, *args,**kwargs):
        self.clearDeadEntities()
        self._process(*args,**kwargs)

CachedWorld = World
