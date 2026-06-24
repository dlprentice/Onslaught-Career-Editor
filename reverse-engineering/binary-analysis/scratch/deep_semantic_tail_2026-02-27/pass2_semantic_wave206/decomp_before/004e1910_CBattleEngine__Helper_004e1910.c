/* address: 0x004e1910 */
/* name: CBattleEngine__Helper_004e1910 */
/* signature: int __thiscall CBattleEngine__Helper_004e1910(void * this, int param_1, int param_2, int param_3) */


int __thiscall CBattleEngine__Helper_004e1910(void *this,int param_1,int param_2,int param_3)

{
  char *pcVar1;

  if (*(char *)((int)this + 4) == '\0') {
    return 0;
  }
  pcVar1 = CSoundManager__Helper_004e2a90((void *)param_1,param_2);
  return (int)pcVar1;
}
