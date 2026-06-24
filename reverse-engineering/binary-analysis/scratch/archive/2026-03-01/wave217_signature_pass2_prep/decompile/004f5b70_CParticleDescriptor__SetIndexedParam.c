/* address: 0x004f5b70 */
/* name: CParticleDescriptor__SetIndexedParam */
/* signature: void __thiscall CParticleDescriptor__SetIndexedParam(void * this, int param_1, int param_2, int param_3) */


void __thiscall CParticleDescriptor__SetIndexedParam(void *this,int param_1,int param_2,int param_3)

{
  *(int *)((int)this + param_1 * 4 + 0xc) = param_2;
  return;
}
