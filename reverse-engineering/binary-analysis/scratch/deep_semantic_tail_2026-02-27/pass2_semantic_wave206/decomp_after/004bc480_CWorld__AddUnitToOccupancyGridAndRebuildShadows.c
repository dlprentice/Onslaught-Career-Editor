/* address: 0x004bc480 */
/* name: CWorld__AddUnitToOccupancyGridAndRebuildShadows */
/* signature: void __cdecl CWorld__AddUnitToOccupancyGridAndRebuildShadows(void * param_1) */


void __cdecl CWorld__AddUnitToOccupancyGridAndRebuildShadows(void *param_1)

{
  float10 fVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iStack_8;

  CSPtrSet__AddToHead(&DAT_00809588,param_1);
  if ((DAT_00809598 != 0) && (DAT_00855290 != 0)) {
    iVar5 = 1;
    fVar1 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
    iStack_8 = (int)(longlong)ROUND(fVar1 + (float10)*(float *)((int)param_1 + 0x20));
    iVar4 = iStack_8;
    fVar1 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
    iStack_8 = (int)(longlong)ROUND(fVar1 + (float10)*(float *)((int)param_1 + 0x1c));
    iVar3 = iStack_8;
    fVar1 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
    iStack_8 = (int)(longlong)ROUND((float10)*(float *)((int)param_1 + 0x20) - fVar1);
    iVar2 = iStack_8;
    fVar1 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
    iStack_8 = (int)(longlong)ROUND((float10)*(float *)((int)param_1 + 0x1c) - fVar1);
    CWorld__RasterizeFootprintIntoOccupancyBitplanes(iStack_8,iVar2,iVar3,iVar4,iVar5);
    CEngine__BuildStaticShadowVolumesAroundUnit(param_1);
  }
  return;
}
