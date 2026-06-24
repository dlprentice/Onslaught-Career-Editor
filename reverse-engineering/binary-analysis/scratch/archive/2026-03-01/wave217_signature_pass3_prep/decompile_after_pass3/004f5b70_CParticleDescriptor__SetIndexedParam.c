/* address: 0x004f5b70 */
/* name: CParticleDescriptor__SetIndexedParam */
/* signature: void __thiscall CParticleDescriptor__SetIndexedParam(void * this, int field_index, int field_value, int unused_flags) */


void __thiscall
CParticleDescriptor__SetIndexedParam(void *this,int field_index,int field_value,int unused_flags)

{
  *(int *)((int)this + field_index * 4 + 0xc) = field_value;
  return;
}
