/* address: 0x00596480 */
/* name: CFastVB__Helper_00596480 */
/* signature: uint __fastcall CFastVB__Helper_00596480(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __fastcall CFastVB__Helper_00596480(void *param_1)

{
  undefined2 in_FPUControlWord;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_8;

  if (DAT_005e6a3c <= *(float *)param_1) {
    if (_DAT_005e6a34 < *(float *)param_1) {
      local_1c = 1.0;
    }
    else {
      local_1c = *(float *)param_1;
    }
  }
  else {
    local_1c = 0.0;
  }
  if (DAT_005e6a3c <= *(float *)((int)param_1 + 4)) {
    if (_DAT_005e6a34 < *(float *)((int)param_1 + 4)) {
      local_18 = 1.0;
    }
    else {
      local_18 = *(float *)((int)param_1 + 4);
    }
  }
  else {
    local_18 = 0.0;
  }
  if (DAT_005e6a3c <= *(float *)((int)param_1 + 8)) {
    if (*(float *)((int)param_1 + 8) <= _DAT_005e6a34) {
      local_14 = *(float *)((int)param_1 + 8);
    }
    else {
      local_14 = 1.0;
    }
  }
  else {
    local_14 = 0.0;
  }
  local_8 = CONCAT22(local_8._2_2_,in_FPUControlWord);
  _DAT_009d241c = local_8;
  return ((int)ROUND(local_1c * _DAT_005e9f00 + _DAT_005e72d4) << 6 |
         (int)ROUND(local_18 * _DAT_005e9ef8 + _DAT_005e72d4)) << 5 |
         (int)ROUND(local_14 * _DAT_005e9f00 + _DAT_005e72d4);
}
