from flask import Blueprint, request, render_template, redirect, url_for, flash, send_from_directory, url_for
from datetime import date, datetime
from foundation_app.extensions import photos
from flask_login import current_user, login_required
from foundation_app.models import Campaign, Donation
from foundation_app.main.forms import CampaignForm, DeleteCampaignForm, DonationForm
from foundation_app.config import Config
from foundation_app.extensions import app, db

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    all_campaigns = Campaign.query.all()
    donation_dict = {}
    for campaign in all_campaigns:
        i = campaign.id
        donation_dict[i] = []
        for donation in campaign.donations:
            donation_dict[i].append(donation.amount)  
    return render_template('home.html', all_campaigns=all_campaigns, donation_dict = donation_dict)

@main.route('/campaigns')
def campaigns():
    all_campaigns = Campaign.query.all()
    donation_dict = {}
    for campaign in all_campaigns:
        i = campaign.id
        donation_dict[i] = []
        for donation in campaign.donations:
            donation_dict[i].append(donation.amount)  
    return render_template('campaigns.html', all_campaigns=all_campaigns, donation_dict = donation_dict)

#PHOTO DISPLAYING
@main.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)
    

@main.route('/new_campaign', methods=['GET', 'POST'])
@login_required
def new_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        #PHOTO HANDLING
        filename = photos.save(form.photo.data) 
        file_url = url_for('main.get_file', filename=filename)

        #CREATE A NEW CAMPAIGN OBJ 
        new_campaign = Campaign (
            name = form.name.data, 
            description = form.description.data,
            photo_url = file_url
        )
            
        db.session.add(new_campaign)
        db.session.commit()
        #did not implement if url is empty !!!!
        flash('New campaign was created successfully.')
        return redirect(url_for('main.homepage'))
    print(form.errors)
    return render_template('new_campaign.html', form = form)


@main.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    form = DonationForm()
    if form.validate_on_submit():
        donation = Donation(
            amount = form.amount.data, 
            donated_by_id = current_user.id,
            donated_to = form.donated_to.data.id
        )

        db.session.add(donation)
        db.session.commit()
        flash('Thank you for your donation!')
        return redirect(url_for('main.homepage'))
    return render_template('donate.html', form = form)

@main.route('/campaign/<campaign_id>', methods=['POST', 'GET'])
def campaign_detail(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    form = CampaignForm(obj = campaign)
    
    if form.validate_on_submit():
        print('form is VALID!')
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)

        #Get path for updated picture as well as rest of info
        campaign.name = form.name.data 
        campaign.description = form.description.data
        campaign.photo_url = file_url

        db.session.commit()
        flash('Campaign updated successfully.')
        return redirect(url_for('main.campaign_detail', campaign_id=campaign_id))
    
    print(form.errors)
    return render_template('campaign_detail.html', campaign=campaign, form=form)


@main.route('/delete_campaign/<campaign_id>', methods=['POST', 'GET'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    form = DeleteCampaignForm(obj = campaign)

    if form.validate_on_submit():
        campaign = Campaign.query.get(campaign_id)
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully.')
        return redirect(url_for('main.homepage'))
    print(form.errors)
    return render_template('campaign_detail.html', campaign=campaign, form=form)


