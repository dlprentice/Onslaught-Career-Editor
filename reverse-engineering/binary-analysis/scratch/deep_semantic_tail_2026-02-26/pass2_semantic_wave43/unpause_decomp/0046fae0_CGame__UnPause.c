/* address: 0x0046fae0 */
/* name: CGame__UnPause */
/* signature: void __fastcall CGame__UnPause(void * this) */


/* Source-aligned with CGame::UnPause(). Clears pause flag; if free-camera is not active for player
   0, deactivates pause menu control path. */

void __fastcall CGame__UnPause(void *this)

{
  int unaff_retaddr;

  *(undefined4 *)((int)this + 0x2c) = 0;
  if (*(int *)((int)this + 0x9d0) == 0) {
    CGillMHead__Unk_004d10b0(*(void **)((int)this + 0x2f4),1,unaff_retaddr);
  }
  return;
}
