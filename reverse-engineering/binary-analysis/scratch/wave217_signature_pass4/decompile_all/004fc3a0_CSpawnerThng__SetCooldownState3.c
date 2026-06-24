/* address: 0x004fc3a0 */
/* name: CSpawnerThng__SetCooldownState3 */
/* signature: void __thiscall CSpawnerThng__SetCooldownState3(void * this, int cooldown_ticks, float unused_scale) */


void __thiscall CSpawnerThng__SetCooldownState3(void *this,int cooldown_ticks,float unused_scale)

{
  *(undefined4 *)((int)this + 0x168) = 3;
  *(float *)((int)this + 0x16c) = DAT_00672fd0 + (float)cooldown_ticks;
  return;
}
