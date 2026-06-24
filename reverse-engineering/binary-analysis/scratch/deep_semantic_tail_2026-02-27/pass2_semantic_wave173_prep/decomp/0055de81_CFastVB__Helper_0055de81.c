/* address: 0x0055de81 */
/* name: CFastVB__Helper_0055de81 */
/* signature: void __cdecl CFastVB__Helper_0055de81(void * param_1, void * param_2) */


void __cdecl CFastVB__Helper_0055de81(void *param_1,void *param_2)

{
  for (; param_1 < param_2; param_1 = (void *)((int)param_1 + 4)) {
    if (*(code **)param_1 != (code *)0x0) {
      (**(code **)param_1)();
    }
  }
  return;
}
