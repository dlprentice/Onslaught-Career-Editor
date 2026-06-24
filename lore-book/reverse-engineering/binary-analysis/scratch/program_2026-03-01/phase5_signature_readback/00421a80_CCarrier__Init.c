/* address: 0x00421a80 */
/* name: CCarrier__Init */
/* signature: void __thiscall CCarrier__Init(void * this, int param_1) */


void __thiscall CCarrier__Init(void *this,int param_1)

{
  undefined4 *puVar1;
  int unaff_EDI;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d186c;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *(undefined4 *)(param_1 + 0x7c) = 2;
  *(undefined4 *)(param_1 + 0x80) = 2;
  *(uint *)(param_1 + 0x70) = *(uint *)(param_1 + 0x70) | 0xa100100;
  CAirUnit__Init(this,param_1);
  puVar1 = (undefined4 *)OID__AllocObject(0x20,0x17,s_C__dev_ONSLAUGHT2_Carrier_cpp_006243bc,0x1a);
  local_4 = 0;
  if (puVar1 == (undefined4 *)0x0) {
    puVar1 = (undefined4 *)0x0;
  }
  else {
    CGuide__ctor_like_0047e290(puVar1,this,unaff_EDI);
    *puVar1 = &PTR_CFrontEndPage__ActiveNotification_NoOp_005d940c;
  }
  local_4 = 0xffffffff;
  *(undefined4 **)((int)this + 0x208) = puVar1;
  puVar1 = (undefined4 *)OID__AllocObject(0x60,0x16,s_C__dev_ONSLAUGHT2_Carrier_cpp_006243bc,0x1b);
  local_4 = 1;
  if (puVar1 != (undefined4 *)0x0) {
    CWarspite__Init(this,param_1);
    *puVar1 = &PTR_LAB_005d93d4;
    *(undefined4 **)((int)this + 0x13c) = puVar1;
    ExceptionList = local_c;
    return;
  }
  *(undefined4 *)((int)this + 0x13c) = 0;
  ExceptionList = local_c;
  return;
}
