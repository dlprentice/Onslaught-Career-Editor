/* address: 0x004bc480 */
/* name: CEngine__Unk_004bc480 */
/* signature: void __cdecl CEngine__Unk_004bc480(void * param_1) */


void __cdecl CEngine__Unk_004bc480(void *param_1)

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
    CExplosionInitThing__Unk_004bd5c0(iStack_8,iVar2,iVar3,iVar4,iVar5);
    CEngine__Unk_004bd9e0(param_1);
  }
  return;
}
