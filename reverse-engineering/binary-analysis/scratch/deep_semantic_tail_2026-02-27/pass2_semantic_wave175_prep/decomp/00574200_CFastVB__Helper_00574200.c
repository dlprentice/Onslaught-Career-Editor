/* address: 0x00574200 */
/* name: CFastVB__Helper_00574200 */
/* signature: void __cdecl CFastVB__Helper_00574200(void * param_1, void * param_2, void * param_3) */


void __cdecl CFastVB__Helper_00574200(void *param_1,void *param_2,void *param_3)

{
  for (; param_1 != param_2; param_1 = (void *)((int)param_1 + 4)) {
    *(undefined4 *)param_3 = *(undefined4 *)param_1;
    param_3 = (void *)((int)param_3 + 4);
  }
  return;
}
