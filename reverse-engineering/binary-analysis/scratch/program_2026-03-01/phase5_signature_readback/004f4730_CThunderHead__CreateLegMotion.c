/* address: 0x004f4730 */
/* name: CThunderHead__CreateLegMotion */
/* signature: void __thiscall CThunderHead__CreateLegMotion(void * this, void * param_1) */


void __thiscall CThunderHead__CreateLegMotion(void *this,void *param_1)

{
  void *this_00;
  int iVar1;
  undefined4 *puVar2;
  void *unaff_ESI;
  char *pcVar3;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d5296;
  pvStack_c = ExceptionList;
  pcVar3 = s_LegMotion_00623074;
  ExceptionList = &pvStack_c;
  this_00 = (void *)(**(code **)(**(int **)((int)this + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(this_00,(int)pcVar3,unaff_ESI);
  if (iVar1 != -1) {
    puVar2 = (undefined4 *)
             OID__AllocObject(0xf0,0x1b,s_C__dev_ONSLAUGHT2_ThunderHead_cp_00633240,0x20);
    iVar1 = 0;
    uStack_4 = 0;
    if (puVar2 == (undefined4 *)0x0) {
      puVar2 = (undefined4 *)0x0;
    }
    else {
      if (this != (void *)0x0) {
        iVar1 = (int)this + 8;
      }
      CMCMech__Constructor(iVar1);
      *puVar2 = &PTR_LAB_005df890;
    }
    *(undefined4 **)((int)this + 0x70) = puVar2;
    uStack_4 = 0xffffffff;
    iVar1 = *(int *)((int)param_1 + 0x3bc);
    CMCMech__SetParams(*(undefined4 *)(iVar1 + 0x144),*(undefined4 *)(iVar1 + 0x148),
                       *(undefined4 *)(iVar1 + 0x14c),0x4059999a,0x3f7d70a4,
                       *(undefined4 *)(iVar1 + 0x150),*(undefined4 *)(iVar1 + 0x140));
    ExceptionList = pvStack_c;
    return;
  }
  *(undefined4 *)((int)this + 0x70) = 0;
  ExceptionList = pvStack_c;
  return;
}
