/* address: 0x005741d0 */
/* name: CFastVB__Helper_005741d0 */
/* signature: void __cdecl CFastVB__Helper_005741d0(void * param_1, void * param_2, void * param_3) */


void __cdecl CFastVB__Helper_005741d0(void *param_1,void *param_2,void *param_3)

{
  for (; param_1 != param_2; param_1 = (void *)((int)param_1 + 2)) {
    *(undefined2 *)param_3 = *(undefined2 *)param_1;
    param_3 = (void *)((int)param_3 + 2);
  }
  return;
}
