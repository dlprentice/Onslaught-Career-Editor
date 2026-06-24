/* address: 0x00573ff0 */
/* name: CFastVB__FillDwordSpanWithValue_00573ff0 */
/* signature: void __stdcall CFastVB__FillDwordSpanWithValue_00573ff0(void * param_1, int param_2, void * param_3) */


void CFastVB__FillDwordSpanWithValue_00573ff0(void *param_1,int param_2,void *param_3)

{
  for (; param_2 != 0; param_2 = param_2 + -1) {
    if (param_1 != (undefined4 *)0x0) {
      *(undefined4 *)param_1 = *(undefined4 *)param_3;
    }
    param_1 = (void *)((int)param_1 + 4);
  }
  return;
}
