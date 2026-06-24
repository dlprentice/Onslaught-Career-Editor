/* address: 0x00573140 */
/* name: CFastVB__CopyWordRange */
/* signature: void __stdcall CFastVB__CopyWordRange(void * param_1, void * param_2, void * param_3) */


void CFastVB__CopyWordRange(void *param_1,void *param_2,void *param_3)

{
  for (; param_1 != param_2; param_1 = (void *)((int)param_1 + 2)) {
    if (param_3 != (undefined2 *)0x0) {
      *(undefined2 *)param_3 = *(undefined2 *)param_1;
    }
    param_3 = (void *)((int)param_3 + 2);
  }
  return;
}
