/* address: 0x0056f4b0 */
/* name: CFastVB__Helper_0056f4b0 */
/* signature: void __thiscall CFastVB__Helper_0056f4b0(void * this, int param_1, void * param_2, void * param_3) */


void __thiscall CFastVB__Helper_0056f4b0(void *this,int param_1,void *param_2,void *param_3)

{
  undefined2 *puVar1;

  puVar1 = *(undefined2 **)((int)this + 8);
  for (; param_2 != puVar1; param_2 = (void *)((int)param_2 + 2)) {
    *(undefined2 *)param_1 = *(undefined2 *)param_2;
    param_1 = param_1 + 2;
  }
  *(int *)((int)this + 8) = param_1;
  return;
}
