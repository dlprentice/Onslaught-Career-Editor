/* address: 0x0050b780 */
/* name: CWorld__DeserializeWorld */
/* signature: undefined CWorld__DeserializeWorld(void) */


void __thiscall CWorld__DeserializeWorld(int param_1,void *param_2)

{
  undefined4 *puVar1;
  int iVar2;
  int unaff_EDI;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d5c1c;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CConsole__Status(&DAT_00663498,s_Deserializing_world_0063d404);
  CMeshPart__Helper_00423910((uint)param_2);
  CMeshPart__Helper_00423910((uint)param_2);
  CMeshPart__Helper_00423960(param_2,param_1 + 0x270,4,1,unaff_EDI);
  CMeshPart__Helper_00423960(param_2,param_1 + 0x26c,4,1,unaff_EDI);
  puVar1 = (undefined4 *)OID__AllocObject(0x28,0x20,s_C__dev_ONSLAUGHT2_world_cpp_0063d2ac,0x284);
  if (puVar1 == (undefined4 *)0x0) {
    puVar1 = (undefined4 *)0x0;
  }
  else {
    puVar1[1] = 0;
    *puVar1 = &PTR_CFrontEndPage__ActiveNotification_NoOp_005d92d4;
    local_4._0_1_ = 1;
    local_4._1_3_ = 0;
    CSPtrSet__Init(puVar1 + 2);
    local_4 = CONCAT31(local_4._1_3_,2);
    CSPtrSet__Init(puVar1 + 6);
    *puVar1 = &PTR_LAB_005dfcb4;
  }
  local_4 = 0xffffffff;
  DAT_0067a748 = puVar1;
  DAT_0067a07c = OID__AllocObject(1,0x80,s_C__dev_ONSLAUGHT2_world_cpp_0063d2ac,0x285);
  DAT_0067a078 = OID__AllocObject(1,0x80,s_C__dev_ONSLAUGHT2_world_cpp_0063d2ac,0x286);
  if (*(int *)(param_1 + 0x270) != -1) {
    CConsole__Status(&DAT_00663498,s_Deserializing_base_world_positio_0063d3e0);
    CMeshPart__Helper_00423910((uint)param_2);
    iVar2 = CWorld__Helper_004239b0((int)param_2);
    *(int *)(param_1 + 0x278) = iVar2;
    CUnitAI__Unk_00423990(param_2);
    CConsole__StatusDone(&DAT_00663498,s_Deserializing_base_world_0063d3c4,'\x01');
  }
  CConsole__Status(&DAT_00663498,s_Deserializing_real_world_0063d3a8);
  CMeshPart__Helper_00423910((uint)param_2);
  iVar2 = CWorld__Helper_004239b0((int)param_2);
  *(int *)(param_1 + 0x274) = iVar2;
  CUnitAI__Unk_00423990(param_2);
  CConsole__StatusDone(&DAT_00663498,s_Deserializing_real_world_positio_0063d384,'\x01');
  CConsole__StatusDone(&DAT_00663498,s_Deserializing_world_0063d404,'\x01');
  ExceptionList = local_c;
  return;
}
