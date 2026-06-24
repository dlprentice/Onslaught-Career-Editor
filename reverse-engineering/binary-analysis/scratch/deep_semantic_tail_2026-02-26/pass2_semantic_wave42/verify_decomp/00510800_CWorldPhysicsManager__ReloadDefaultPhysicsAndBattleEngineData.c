/* address: 0x00510800 */
/* name: CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData */
/* signature: void CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData(void)

{
  void *pvVar1;
  int iVar2;
  char *pcVar3;
  char *pcVar4;
  undefined4 *puVar5;
  void *local_18c;
  void *local_188;
  char local_184 [28];
  undefined4 local_168 [10];
  undefined1 local_140 [308];
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d661f;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CWorldPhysicsManager__ClearAndFreeAllDefinitionLists();
  CWorldPhysicsManager__InitializeLists();
  pcVar3 = s_data_default_physics_dat_0063daac;
  pcVar4 = local_184;
  for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
    *(undefined4 *)pcVar4 = *(undefined4 *)pcVar3;
    pcVar3 = pcVar3 + 4;
    pcVar4 = pcVar4 + 4;
  }
  *pcVar4 = *pcVar3;
  CChunker__CChunker();
  local_4 = 0;
  iVar2 = DXMemBuffer__OpenRead(local_184,0x11,1,0);
  if (iVar2 != 0) {
    CPhysicsScript__Load(local_140);
    CPhysicsScript__Update();
    CPhysicsScript__Destroy();
    DXMemBuffer__Close();
  }
  pvVar1 = CSPtrSet__First(&DAT_006602a0);
  while (pvVar1 != (void *)0x0) {
    CSPtrSet__Remove(&DAT_006602a0,pvVar1);
    CBattleEngineDataManager__Clear();
    local_18c = pvVar1;
    if (pvVar1 != (void *)0x0) {
      local_4._0_1_ = 1;
      CSPtrSet__Clear((void *)((int)pvVar1 + 0x50));
      local_4 = (uint)local_4._1_3_ << 8;
      CSPtrSet__Clear((void *)((int)pvVar1 + 0x40));
      OID__FreeObject(pvVar1);
    }
    pvVar1 = CSPtrSet__First(&DAT_006602a0);
  }
  local_18c = (void *)OID__AllocObject(0xac,0x15,s_C__dev_ONSLAUGHT2_BattleEngineDa_0063da80,0x107);
  local_4._0_1_ = 2;
  if (local_18c == (void *)0x0) {
    pvVar1 = (void *)0x0;
  }
  else {
    pvVar1 = (void *)CSPtrSet_Init__Wrapper_0040f520((int)local_18c);
  }
  local_4 = (uint)local_4._1_3_ << 8;
  CBattleEngineDataManager__Init();
  CSPtrSet__AddToHead(&DAT_006602a0,pvVar1);
  pcVar3 = s_data_battle_engine_configuration_0063da58;
  puVar5 = local_168;
  for (iVar2 = 9; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar5 = *(undefined4 *)pcVar3;
    pcVar3 = pcVar3 + 4;
    puVar5 = puVar5 + 1;
  }
  *(undefined2 *)puVar5 = *(undefined2 *)pcVar3;
  iVar2 = DXMemBuffer__OpenRead(local_168,0x11,1,0);
  if (iVar2 == 0) {
    FatalError__ExitWithLocalizedPrefix_A(local_168);
  }
  else {
    while ((_DAT_006602a8 = DAT_006602a0, DAT_006602a0 != (undefined4 *)0x0 &&
           (pvVar1 = (void *)*DAT_006602a0, pvVar1 != (void *)0x0))) {
      CSPtrSet__Remove(&DAT_006602a0,pvVar1);
      CBattleEngineDataManager__Clear();
      local_4._0_1_ = 3;
      local_188 = pvVar1;
      CSPtrSet__Clear((void *)((int)pvVar1 + 0x50));
      local_4 = (uint)local_4._1_3_ << 8;
      CSPtrSet__Clear((void *)((int)pvVar1 + 0x40));
      OID__FreeObject(pvVar1);
    }
    DXMemBuffer__ReadBytes(&local_18c,4);
    iVar2 = 0;
    if (0 < (int)local_18c) {
      do {
        local_188 = (void *)OID__AllocObject(0xac,0x15,s_C__dev_ONSLAUGHT2_BattleEngineDa_0063da80,
                                             0x136);
        local_4._0_1_ = 4;
        if (local_188 == (void *)0x0) {
          pvVar1 = (void *)0x0;
        }
        else {
          pvVar1 = (void *)CSPtrSet_Init__Wrapper_0040f520((int)local_188);
        }
        local_4 = (uint)local_4._1_3_ << 8;
        CBattleEngineDataManager__Init();
        CBattleEngineDataManager__Load(local_140);
        CSPtrSet__AddToHead(&DAT_006602a0,pvVar1);
        iVar2 = iVar2 + 1;
      } while (iVar2 < (int)local_18c);
    }
    DXMemBuffer__Close();
  }
  local_4 = 0xffffffff;
  CChunker__Destructor();
  ExceptionList = local_c;
  return;
}
