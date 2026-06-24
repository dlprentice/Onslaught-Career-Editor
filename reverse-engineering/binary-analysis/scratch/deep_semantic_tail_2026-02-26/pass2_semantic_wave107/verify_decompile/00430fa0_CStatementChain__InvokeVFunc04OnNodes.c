/* address: 0x00430fa0 */
/* name: CStatementChain__InvokeVFunc04OnNodes */
/* signature: void __thiscall CStatementChain__InvokeVFunc04OnNodes(void * this, int param_1, int param_2) */


void __thiscall CStatementChain__InvokeVFunc04OnNodes(void *this,int param_1,int param_2)

{
  do {
    if (*(int **)((int)this + 4) != (int *)0x0) {
      (**(code **)(**(int **)((int)this + 4) + 4))(param_1);
    }
    this = *(void **)((int)this + 8);
  } while (this != (void *)0x0);
  return;
}
