/* address: 0x005736a0 */
/* name: MemCopyU16Elements */
/* signature: void __stdcall MemCopyU16Elements(void * param_1, int param_2, void * param_3) */


void MemCopyU16Elements(void *param_1,int param_2,void *param_3)

{
  for (; param_2 != 0; param_2 = param_2 + -1) {
    if (param_1 != (undefined2 *)0x0) {
      *(undefined2 *)param_1 = *(undefined2 *)param_3;
    }
    param_1 = (void *)((int)param_1 + 2);
  }
  return;
}
