/* address: 0x0055e598 */
/* name: ControlsUI__Helper_0055e598 */
/* signature: int __cdecl ControlsUI__Helper_0055e598(void * param_1, int param_2) */


int __cdecl ControlsUI__Helper_0055e598(void *param_1,int param_2)

{
  int iVar1;
  undefined1 *local_24;
  int local_20;
  void *local_1c;
  undefined4 local_18;

  local_1c = param_1;
  local_24 = param_1;
  local_18 = 0x42;
  local_20 = 0x7fffffff;
  iVar1 = ControlsUI__Helper_00565083((int)&local_24,(void *)param_2,&stack0x0000000c);
  local_20 = local_20 + -1;
  if (local_20 < 0) {
    CRT__FlsBuf(0,&local_24);
  }
  else {
    *local_24 = 0;
    local_24 = local_24 + 1;
  }
  local_20 = local_20 + -1;
  if (local_20 < 0) {
    CRT__FlsBuf(0,&local_24);
  }
  else {
    *local_24 = 0;
  }
  return iVar1;
}
