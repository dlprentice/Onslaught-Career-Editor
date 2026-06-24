/* address: 0x004fc3a0 */
/* name: CSpawnerThng__SetCooldownState3 */
/* signature: void __thiscall CSpawnerThng__SetCooldownState3(void * this, int param_1, float param_2) */


void __thiscall CSpawnerThng__SetCooldownState3(void *this,int param_1,float param_2)

{
  *(undefined4 *)((int)this + 0x168) = 3;
  *(float *)((int)this + 0x16c) = DAT_00672fd0 + (float)param_1;
  return;
}
