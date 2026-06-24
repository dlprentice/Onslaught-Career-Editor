/* address: 0x0047fe30 */
/* name: CHiveBoss__Init */
/* signature: undefined CHiveBoss__Init(void) */


void __thiscall CHiveBoss__Init(void *param_1,int param_2)

{
  int iVar1;
  void *this;
  undefined4 *this_00;
  int unaff_EDI;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d2cf2;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *(uint *)(param_2 + 0x70) = *(uint *)(param_2 + 0x70) | 0xa100000;
  *(undefined4 *)(param_2 + 0x7c) = 2;
  *(undefined4 *)(param_2 + 0x80) = 2;
  iVar1 = OID__AllocObject(0x30,0x55,s_C__dev_ONSLAUGHT2_HiveBoss_cpp_0062cc98,0x21);
  local_4 = 0;
  if (iVar1 == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CDestroyableSegment__Unk_00443fc0();
  }
  local_4 = 0xffffffff;
  *(int *)((int)param_1 + 0x178) = iVar1;
  this = (void *)OID__AllocObject(0x78,0x1b,s_C__dev_ONSLAUGHT2_HiveBoss_cpp_0062cc98,0x22);
  local_4 = 1;
  if (this == (void *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = CMCHiveBoss__ctor_like_00497090(this,param_1,unaff_EDI);
  }
  local_4 = 0xffffffff;
  *(int *)((int)param_1 + 0x70) = iVar1;
  CUnit__Init(param_2);
  iVar1 = CDestroyableSegment__Unk_00444520(*(void **)((int)param_1 + 0x178),0x62cc90,unaff_EDI);
  *(int *)((int)param_1 + 0x2a4) = iVar1;
  this_00 = (undefined4 *)OID__AllocObject(0x2c,0x17,s_C__dev_ONSLAUGHT2_HiveBoss_cpp_0062cc98,0x28)
  ;
  local_4 = 2;
  if (this_00 == (undefined4 *)0x0) {
    this_00 = (undefined4 *)0x0;
  }
  else {
    CGuide__ctor_like_0047e290(this_00,param_1,unaff_EDI);
    *this_00 = &PTR_CFrontEndPage__ActiveNotification_NoOp_005dbe08;
    this_00[8] = 0x3ca3d70a;
    this_00[9] = 0x3ca3d70a;
    this_00[10] = 0x3ca3d70a;
  }
  *(undefined4 **)((int)param_1 + 0x208) = this_00;
  *(undefined4 *)((int)param_1 + 0x250) = 0;
  *(undefined4 *)((int)param_1 + 0x254) = 0;
  *(undefined4 *)((int)param_1 + 600) = 0;
  *(undefined4 *)((int)param_1 + 0x25c) = 0;
  *(undefined4 *)((int)param_1 + 0x260) = 0;
  *(undefined4 *)((int)param_1 + 0x264) = 0;
  *(undefined4 *)((int)param_1 + 0x268) = 0xbf800000;
  *(undefined4 *)((int)param_1 + 0x284) = 0;
  *(undefined4 *)((int)param_1 + 0x288) = 0;
  *(undefined4 *)((int)param_1 + 0x28c) = 0;
  *(undefined4 *)((int)param_1 + 0x290) = 0;
  *(undefined4 *)((int)param_1 + 0x294) = 0;
  *(undefined4 *)((int)param_1 + 0x298) = 0;
  *(undefined4 *)((int)param_1 + 0x2a0) = 0x41f00000;
  *(undefined4 *)((int)param_1 + 0x29c) = 0;
  *(undefined4 *)((int)param_1 + 300) = 0x41200000;
  *(undefined4 *)((int)param_1 + 0x130) = 0;
  *(undefined4 *)((int)param_1 + 0x134) = 0;
  ExceptionList = local_c;
  return;
}
