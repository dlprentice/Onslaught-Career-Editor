/* address: 0x004a3630 */
/* name: CMenuItem__InitWithIcon */
/* signature: undefined CMenuItem__InitWithIcon(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 * __thiscall
CMenuItem__InitWithIcon
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,float param_4,int param_5,
          int param_6,undefined1 param_7)

{
  undefined3 uVar1;
  void *this;
  undefined4 local_14;
  void *local_c;
  undefined1 *puStack_8;
  undefined1 local_4;
  undefined3 uStack_3;

  puStack_8 = &LAB_005d3686;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  param_1[1] = param_3;
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = 1;
  param_1[5] = 0xffd6d6d6;
  param_1[6] = param_2;
  *param_1 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
  param_1[7] = 0;
  param_1[8] = 0;
  *(undefined1 *)(param_1 + 0xc) = param_7;
  uStack_3 = 0;
  uVar1 = uStack_3;
  local_4 = 1;
  uStack_3 = 0;
  param_1[0xd] = param_5;
  if (param_5 != 0) {
    if (*(int *)(param_5 + 4) == 0) {
      this = (void *)OID__AllocObject(0x10,0x5e,s_C__dev_ONSLAUGHT2_Monitor_h_00622b80,0x18);
      local_4 = 2;
      if (this == (void *)0x0) {
        this = (void *)0x0;
      }
      else {
        CSPtrSet__Init(this);
      }
      *(void **)(param_5 + 4) = this;
      uVar1 = uStack_3;
    }
    uStack_3 = uVar1;
    local_4 = 1;
    CSPtrSet__AddToHead(*(void **)(param_5 + 4),param_1 + 0xd);
  }
  param_1[0xb] = param_6;
  *param_1 = &PTR_CMenuItem__ScalarDestructor_005dc520;
  local_14 = (undefined4)(longlong)ROUND((float)param_6 * param_4 + _DAT_005dc560);
  param_1[9] = local_14;
  param_1[10] = local_14;
  ExceptionList = local_c;
  return param_1;
}
