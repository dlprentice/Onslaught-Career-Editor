/* address: 0x004725f0 */
/* name: CGame__GetPlayerLives */
/* signature: int __thiscall CGame__GetPlayerLives(void * this, int param_1, int param_2) */


int __thiscall CGame__GetPlayerLives(void *this,int param_1,int param_2)

{
  if (param_1 == 1) {
    return *(int *)((int)this + 0x290);
  }
  if (param_1 == 2) {
    return *(int *)((int)this + 0x294);
  }
  return 0;
}
