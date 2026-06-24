/* address: 0x004f39b0 */
/* name: CUnit__DebugTraceIfFlag30Set */
/* signature: void __thiscall CUnit__DebugTraceIfFlag30Set(void * this, int param_1, void * param_2) */


void __thiscall CUnit__DebugTraceIfFlag30Set(void *this,int param_1,void *param_2)

{
  if (*(int *)((int)this + 0x30) != 0) {
    DebugTrace((char *)param_1);
    return;
  }
  return;
}
