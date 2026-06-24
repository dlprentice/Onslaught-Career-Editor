/* address: 0x0049f940 */
/* name: CMech__InitLegMotion */
/* signature: void __thiscall CMech__InitLegMotion(void * this) */


void __thiscall CMech__InitLegMotion(void *this)

{
  void *this_00;
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  void *unaff_ESI;
  int in_stack_00000004;
  char *pcVar4;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d33d6;
  pvStack_c = ExceptionList;
  pcVar4 = s_LegMotion_00623074;
  ExceptionList = &pvStack_c;
  this_00 = (void *)(**(code **)(**(int **)((int)this + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(this_00,(int)pcVar4,unaff_ESI);
  if (iVar1 != -1) {
    iVar2 = OID__AllocObject(0xf0,0x1b,s_C__dev_ONSLAUGHT2_Mech_cpp_0062e0e0,0x3d);
    iVar1 = 0;
    uStack_4 = 0;
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      if (this != (void *)0x0) {
        iVar1 = (int)this + 8;
      }
      uVar3 = CMCMech__Constructor(iVar1);
    }
    *(undefined4 *)((int)this + 0x70) = uVar3;
    uStack_4 = 0xffffffff;
    iVar1 = *(int *)(in_stack_00000004 + 0x3bc);
    CMCMech__SetParams(*(undefined4 *)(iVar1 + 0x144),*(undefined4 *)(iVar1 + 0x148),
                       *(undefined4 *)(iVar1 + 0x14c),0x3ecccccd,0x3f666666,
                       *(undefined4 *)(iVar1 + 0x150),*(undefined4 *)(iVar1 + 0x140));
    ExceptionList = pvStack_c;
    return;
  }
  *(undefined4 *)((int)this + 0x70) = 0;
  ExceptionList = pvStack_c;
  return;
}
