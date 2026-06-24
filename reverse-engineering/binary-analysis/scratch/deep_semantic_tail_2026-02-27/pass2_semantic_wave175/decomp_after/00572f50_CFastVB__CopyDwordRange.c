/* address: 0x00572f50 */
/* name: CFastVB__CopyDwordRange */
/* signature: void __stdcall CFastVB__CopyDwordRange(void * param_1, void * param_2, void * param_3) */


void CFastVB__CopyDwordRange(void *param_1,void *param_2,void *param_3)

{
  for (; param_1 != param_2; param_1 = (void *)((int)param_1 + 4)) {
    if (param_3 != (undefined4 *)0x0) {
      *(undefined4 *)param_3 = *(undefined4 *)param_1;
    }
    param_3 = (void *)((int)param_3 + 4);
  }
  return;
}
