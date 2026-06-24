/* address: 0x004f3970 */
/* name: CThing__SetObjective */
/* signature: void __thiscall CThing__SetObjective(void * this, void * param_1, int param_2) */


void __thiscall CThing__SetObjective(void *this,void *param_1,int param_2)

{
  if (param_1 == (void *)0x1) {
    if ((*(byte *)((int)this + 0x2c) & 0x20) == 0) {
      CSPtrSet__AddToHead(&DAT_00855140,this);
      *(byte *)((int)this + 0x2c) = *(byte *)((int)this + 0x2c) | 0x20;
      return;
    }
  }
  else if ((*(byte *)((int)this + 0x2c) & 0x20) != 0) {
    CSPtrSet__Remove(&DAT_00855140,this);
    *(byte *)((int)this + 0x2c) = *(byte *)((int)this + 0x2c) & 0xdf;
  }
  return;
}
