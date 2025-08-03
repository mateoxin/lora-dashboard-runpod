import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoraTabComponent } from './lora-tab.component';

describe('LoraTabComponent', () => {
  let component: LoraTabComponent;
  let fixture: ComponentFixture<LoraTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoraTabComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LoraTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
