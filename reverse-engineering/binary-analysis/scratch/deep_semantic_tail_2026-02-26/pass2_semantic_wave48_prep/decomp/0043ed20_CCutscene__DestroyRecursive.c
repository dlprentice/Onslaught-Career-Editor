/* address: 0x0043ed20 */
/* name: CCutscene__DestroyRecursive */
/* signature: void * __thiscall CCutscene__DestroyRecursive(void * this, void * param_1, int param_2) */


void * __thiscall CCutscene__DestroyRecursive(void *this,void *param_1,int param_2)

{
  int unaff_ESI;

  if (*(undefined4 **)((int)this + 0x244) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)this + 0x244))(1);
  }
  *(undefined4 *)((int)this + 0x244) = 0;
  if (*(void **)((int)this + 0x248) != (void *)0x0) {
    CCutscene__DestroyRecursive(*(void **)((int)this + 0x248),(void *)0x1,unaff_ESI);
  }
  *(undefined4 *)((int)this + 0x248) = 0;
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
