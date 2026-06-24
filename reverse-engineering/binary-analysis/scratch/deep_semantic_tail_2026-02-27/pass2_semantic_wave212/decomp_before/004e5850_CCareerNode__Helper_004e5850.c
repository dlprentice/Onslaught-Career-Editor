/* address: 0x004e5850 */
/* name: CCareerNode__Helper_004e5850 */
/* signature: int __thiscall CCareerNode__Helper_004e5850(void * this, void * param_1, void * param_2) */


int __thiscall CCareerNode__Helper_004e5850(void *this,void *param_1,void *param_2)

{
  undefined4 *puVar1;
  void *item;

  *(undefined4 *)this = 0;
  *(undefined4 *)((int)this + 4) = 0;
  *(undefined4 *)((int)this + 0xc) = 0;
  puVar1 = *(undefined4 **)param_1;
  if (puVar1 != (undefined4 *)0x0) {
    item = (void *)*puVar1;
    while (item != (void *)0x0) {
      CSPtrSet__AddToTail(this,item);
      puVar1 = (undefined4 *)puVar1[1];
      if (puVar1 == (undefined4 *)0x0) {
        return (int)this;
      }
      item = (void *)*puVar1;
    }
  }
  return (int)this;
}
