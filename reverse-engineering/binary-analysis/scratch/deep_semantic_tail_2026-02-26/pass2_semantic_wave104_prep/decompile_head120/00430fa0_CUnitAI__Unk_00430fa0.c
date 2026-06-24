/* address: 0x00430fa0 */
/* name: CUnitAI__Unk_00430fa0 */
/* signature: void __thiscall CUnitAI__Unk_00430fa0(void * this, int param_1, int param_2) */


void __thiscall CUnitAI__Unk_00430fa0(void *this,int param_1,int param_2)

{
  do {
    if (*(int **)((int)this + 4) != (int *)0x0) {
      (**(code **)(**(int **)((int)this + 4) + 4))(param_1);
    }
    this = *(void **)((int)this + 8);
  } while (this != (void *)0x0);
  return;
}
