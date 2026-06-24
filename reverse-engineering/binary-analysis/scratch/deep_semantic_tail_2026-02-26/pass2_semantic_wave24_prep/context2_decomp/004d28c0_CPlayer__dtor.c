/* address: 0x004d28c0 */
/* name: CPlayer__dtor */
/* signature: undefined CPlayer__dtor(void) */


void __fastcall CPlayer__dtor(int param_1)

{
  int iVar1;
  undefined3 uVar2;
  undefined4 *camera;
  void *this;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d476c;
  local_c = ExceptionList;
  if (*(int *)(param_1 + 0x1c) != 0) {
    ExceptionList = &local_c;
    *(undefined4 *)(param_1 + 0x24) = 1;
    camera = (undefined4 *)OID__AllocObject(8,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0x3a);
    if (camera == (undefined4 *)0x0) {
      camera = (undefined4 *)0x0;
    }
    else {
      iVar1 = *(int *)(param_1 + 0x1c);
      *camera = &PTR_LAB_005d9260;
      local_4._1_3_ = 0;
      uVar2 = local_4._1_3_;
      local_4._0_1_ = 2;
      local_4._1_3_ = 0;
      camera[1] = iVar1;
      if (iVar1 != 0) {
        if (*(int *)(iVar1 + 4) == 0) {
          this = (void *)OID__AllocObject(0x10,0x5e,s_C__dev_ONSLAUGHT2_monitor_h_0062551c,0x18);
          local_4._0_1_ = 3;
          if (this == (void *)0x0) {
            this = (void *)0x0;
          }
          else {
            CSPtrSet__Init(this);
          }
          *(void **)(iVar1 + 4) = this;
          uVar2 = local_4._1_3_;
        }
        local_4._1_3_ = uVar2;
        local_4._0_1_ = 2;
        CSPtrSet__AddToHead(*(void **)(iVar1 + 4),camera + 1);
      }
      *camera = &PTR_LAB_005dbb88;
    }
    local_4 = 0xffffffff;
    CGame__SetCurrentCamera(&DAT_008a9a98,*(int *)(param_1 + 0x2c) + -1,camera,'\x01');
  }
  ExceptionList = local_c;
  return;
}
