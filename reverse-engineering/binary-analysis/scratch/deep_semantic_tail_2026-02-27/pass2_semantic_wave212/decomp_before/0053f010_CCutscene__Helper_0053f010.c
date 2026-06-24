/* address: 0x0053f010 */
/* name: CCutscene__Helper_0053f010 */
/* signature: void __thiscall CCutscene__Helper_0053f010(void * this, int param_1, int param_2, int param_3) */


void __thiscall CCutscene__Helper_0053f010(void *this,int param_1,int param_2,int param_3)

{
  if ((char)param_2 != '\0') {
    *(int *)((int)this + 0x4cc) = param_1;
    return;
  }
  *(int *)((int)this + 0x4d0) = param_1;
  return;
}
